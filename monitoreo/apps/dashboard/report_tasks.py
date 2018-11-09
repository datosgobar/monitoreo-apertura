# coding=utf-8
from __future__ import unicode_literals

from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django_rq import job

from pydatajson.core import DataJson
from django_datajsonar.models import Node

from .models import Indicador, IndicadorRed, \
    IndicatorsGenerationTask, ReportGenerationTask, ValidationReportTask


@job('reports')
def send_reports(report_task=None):
    try:
        indicators_task = IndicatorsGenerationTask.objects\
            .filter(status=IndicatorsGenerationTask.FINISHED).latest('finished')
    except IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return

    report_task = report_task or ReportGenerationTask.objects.create()

    generator = IndicatorReportGenerator(indicators_task, report_task)
    mail = generator.generate_email()
    generator.send_email(mail)

    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        mail = generator.generate_email(node)
        if mail:
            generator.send_email(mail, node=node)
    generator.close_task()


@job('reports')
def send_validations(validation_task=None):
    validation_task = validation_task or ValidationReportTask.objects.create()

    generator = ValidationReportGenerator(validation_task)
    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        mail = generator.generate_email(node)
        if mail:
            generator.send_email(mail, node=node)
    generator.close_task()


class AbstractReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    TXT_TEMPLATE = None
    HTML_TEMPLATE = None

    def __init__(self, report_task):
        self.report_task = report_task

    def generate_email(self, *args, **kwargs):
        raise NotImplementedError

    def send_email(self, mail, node=None):
        target = node.catalog_id if node else 'Red'

        try:
            mail.send()
            msg = "Reporte de {} enviado exitosamente".format(target)
        except SMTPException as e:
            msg = "Error enviando reporte de {}:\n {}".format(target, str(e))

        self.report_task.info(self.report_task, msg)

    def _get_recipients(self, node=None):
        if not node:
            recipients = User.objects.filter(is_staff=True)
        else:
            recipients = node.admins.all()
        return [user.email for user in recipients if user.email]

    def _render_templates(self, subject, emails, context):
        msg = render_to_string(self.TXT_TEMPLATE, context=context)
        html_msg = render_to_string(self.HTML_TEMPLATE, context=context)
        mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER, emails)
        mail.attach_alternative(html_msg, 'text/html')
        return mail

    def close_task(self):
        self.report_task.refresh_from_db()
        self.report_task.status = self.report_task.FINISHED
        self.report_task.finished = timezone.now()
        self.report_task.save()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)


class IndicatorReportGenerator(AbstractReportGenerator):
    TXT_TEMPLATE = 'reports/report.txt'
    HTML_TEMPLATE = 'reports/report.html'

    def __init__(self, indicators_task, report_task):
        self.indicators_task = indicators_task
        super(IndicatorReportGenerator, self).__init__(report_task)

    def generate_email(self, node=None):
        """Genera y manda el mail con el reporte de indexación. Si node es especificado, genera el reporte
        con valores de entidades pertenecientes únicamente a ese nodo (reporte individual). Caso contrario
        (default), genera el reporte de indexación global
        """

        context = {
            'finish_time': self._format_date(self.indicators_task.finished)
        }
        if not node:
            one_d_summary, multi_d_summary, _ = \
                IndicadorRed.objects.filter(indicador_tipo__resumen=True).\
                sorted_indicators_on_date(
                    self.indicators_task.finished
                    .astimezone(timezone.get_current_timezone())
                    .date())
            one_dimensional, multi_dimensional, listed = \
                IndicadorRed.objects.filter(indicador_tipo__mostrar=True).\
                sorted_indicators_on_date(
                    self.indicators_task.finished
                    .astimezone(timezone.get_current_timezone())
                    .date())
        else:
            one_d_summary, multi_d_summary, _ = \
                Indicador.objects.filter(indicador_tipo__resumen=True).\
                sorted_indicators_on_date(
                    self.indicators_task.finished
                    .astimezone(timezone.get_current_timezone())
                    .date(), node)
            one_dimensional, multi_dimensional, listed = \
                Indicador.objects.filter(indicador_tipo__mostrar=True)\
                .sorted_indicators_on_date(
                    self.indicators_task.finished
                    .astimezone(timezone.get_current_timezone())
                    .date(), node)

        context.update({
            'one_d_summary': one_d_summary,
            'multi_d_summary': multi_d_summary,
            'one_dimensional_indics': one_dimensional,
            'multi_dimensional_indics': multi_dimensional,
        })

        emails = self._get_recipients(node=node)
        if not emails:
            # Nothing to do here
            return None
        start_time = self._format_date(self.indicators_task.created)
        subject = u'[{}] Indicadores Monitoreo Apertura: {}'.format(settings.ENV_TYPE, start_time)
        mail = self._render_templates(subject, emails, context)

        if not node:
            mail.attach('info.log', self.indicators_task.logs, 'text/plain')

        for indicator in listed:
            if listed[indicator]:
                body = render_to_string('reports/datasets.csv', context={'dataset_list': listed[indicator]})
                mail.attach('{}.csv'.format(indicator), body, 'text/csv')

        return mail


class ValidationReportGenerator(AbstractReportGenerator):
    TXT_TEMPLATE = 'reports/validation.txt'
    HTML_TEMPLATE = 'reports/validation.html'

    def __init__(self, report_task):
        self.report_task = report_task
        super(ValidationReportGenerator, self).__init__(report_task)

    def generate_email(self, node):
        catalog = DataJson(node.catalog_url)
        validation = catalog.validate_catalog(only_errors=True)
        if validation['status'] == 'OK':
            return None
        context = {
            'validation_time': self._format_date(timezone.now()),
            'status': validation['status'],
            'catalog': validation['error']['catalog'],
            'dataset_list': validation['error']['dataset']
        }

        subject = u'[{}] Validacion de {}'.format(settings.ENV_TYPE, node.catalog_id)
        emails = self._get_recipients(node=node)
        if not emails:
            # Nothing to do here
            return None
        mail = self._render_templates(subject, emails, context)

        return mail

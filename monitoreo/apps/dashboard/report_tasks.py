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

from . import models


@job('reports')
def send_reports(report_task=None):
    try:
        indicators_task = models.IndicatorsGenerationTask.objects\
            .filter(status=models.IndicatorsGenerationTask.FINISHED).latest('finished')
    except models.IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return

    report_task = report_task or models.ReportGenerationTask.objects.create()

    generator = IndicatorReportGenerator(indicators_task, report_task)
    mail = generator.generate_email()
    generator.send_email(mail)

    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        mail = generator.generate_email(node)
        generator.send_email(mail, node=node)
    generator.close_task()


@job('reports')
def send_validations(validation_task=None):
    validation_task = validation_task or models.ValidationReportTask.objects.create()
    generator = ValidationReportGenerator(validation_task)
    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        mail = generator.generate_email(node=node)
        if mail:
            generator.send_email(mail, node=node)
    generator.close_task()


class ReportSender(object):
    def __init__(self, report_task):
        self.report_task = report_task

    def _get_recipients(self, node=None):
        if not node:
            recipients = User.objects.filter(is_staff=True)
        else:
            recipients = node.admins.all()
        return [user.email for user in recipients if user.email]

    def send_email(self, mail, node=None):
        target = node.catalog_id if node else 'Red'
        mail.to = self._get_recipients(node=node)
        try:
            mail.send()
            msg = "Reporte de {} enviado exitosamente".format(target)
        except SMTPException as e:
            msg = "Error enviando reporte de {}:\n {}".format(target, str(e))
        self.report_task.info(self.report_task, msg)


class AbstractReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, report_task):
        self.report_task = report_task
        self.sender = ReportSender(report_task)

    def generate_email(self, node=None):
        raise NotImplementedError

    def close_task(self):
        self.report_task.refresh_from_db()
        self.report_task.status = self.report_task.FINISHED
        self.report_task.finished = timezone.now()
        self.report_task.save()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    def send_email(self, mail, node=None):
        self.sender.send_email(mail, node=node)


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
            'finish_time': self._format_date(self.indicators_task.finished),
            'target': node.catalog_id if node else 'Red'
        }
        model = models.Indicador if node else models.IndicadorRed

        queryset = model.objects.filter(indicador_tipo__resumen=True)
        context['one_d_summary'], context['multi_d_summary'], _ =\
            self._get_current_indicators(queryset, node=node)

        queryset = model.objects.filter(indicador_tipo__mostrar=True)
        context['one_dimensional_indics'], context['multi_dimensional_indics'], context['listed'] = \
            self._get_current_indicators(queryset, node=node)

        start_time = self._format_date(self.indicators_task.created)
        subject = u'[{}] Indicadores Monitoreo Apertura: {}'.format(settings.ENV_TYPE, start_time)
        mail = self._render_templates(subject, context)

        listed = context['listed']
        if not node:
            mail.attach('info.log', self.indicators_task.logs, 'text/plain')
        for indicator in listed:
            if listed[indicator]:
                body = render_to_string('reports/datasets.csv', context={'dataset_list': listed[indicator]})
                mail.attach('{}.csv'.format(indicator), body, 'text/csv')
        return mail

    def _get_current_indicators(self, queryset, node=None):
        return queryset.sorted_indicators_on_date(
            self.indicators_task.finished.astimezone(
                timezone.get_current_timezone()).date(),
            node)

    def _render_templates(self, subject, context):
        msg = render_to_string(self.TXT_TEMPLATE, context=context)
        html_msg = render_to_string(self.HTML_TEMPLATE, context=context)
        mail = EmailMultiAlternatives(subject, msg,
                                      settings.EMAIL_HOST_USER)
        mail.attach_alternative(html_msg, 'text/html')
        return mail


class ValidationReportGenerator(AbstractReportGenerator):
    TXT_TEMPLATE = 'reports/validation.txt'
    HTML_TEMPLATE = 'reports/validation.html'

    def __init__(self, report_task):
        self.report_task = report_task
        super(ValidationReportGenerator, self).__init__(report_task)

    def generate_email(self, node=None):
        if not node:
            # No genera mail de staff
            return None
        catalog = DataJson(node.catalog_url)
        validation = catalog.validate_catalog(only_errors=True)
        if validation['status'] == 'OK':
            msg = "Catálogo {} válido.".format(node.catalog_id)
            self.report_task.info(self.report_task, msg)
            return None
        context = {
            'validation_time': self._format_date(timezone.now()),
            'status': validation['status'],
            'catalog': validation['error']['catalog'],
            'dataset_list': validation['error']['dataset']
        }

        subject = u'[{}] Validacion de {}'.format(settings.ENV_TYPE, node.catalog_id)
        mail = self._render_templates(subject, context)

        return mail

    def _render_templates(self, subject, context):
        msg = render_to_string(self.TXT_TEMPLATE, context=context)
        html_msg = render_to_string(self.HTML_TEMPLATE, context=context)
        mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER)
        mail.attach_alternative(html_msg, 'text/html')
        return mail

# coding=utf-8
from __future__ import unicode_literals

import os
from smtplib import SMTPException
from tempfile import NamedTemporaryFile

from requests.exceptions import RequestException

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django_rq import job
from des.models import DynamicEmailConfiguration

from pydatajson.core import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog
from django_datajsonar.models import Node

from . import models


@job('reports')
def send_reports(node=None):
    report_task = models.ReportGenerationTask.objects.create()
    indicators_run(report_task, node=node)


@job('reports')
def send_validations(node=None):
    validation_task = models.ValidationReportTask.objects.create()
    validation_run(validation_task, node=node)


@job('reports')
def indicators_run(report_task, node=None):
    try:
        indicators_task = models.IndicatorsGenerationTask.objects\
            .filter(status=models.IndicatorsGenerationTask.FINISHED).latest('finished')
    except models.IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return

    generator = IndicatorReportGenerator(indicators_task, report_task)
    mail = generator.generate_email()
    generator.send_email(mail)

    nodes = [node] if node else Node.objects.filter(indexable=True)
    for target_node in nodes:
        mail = generator.generate_email(target_node)
        generator.send_email(mail, node=target_node)
    generator.close_task()


@job('reports')
def validation_run(validation_task, node=None):
    generator = ValidationReportGenerator(validation_task)
    nodes = [node] if node else Node.objects.filter(indexable=True)
    for target_node in nodes:
        try:
            mail = generator.generate_email(node=target_node)
        except (NonParseableCatalog, RequestException) as e:
            msg = 'Error enviando la validación de {}: {}'\
                .format(target_node.catalog_id, str(e))
            models.ValidationReportTask.info(validation_task, msg)
            mail = generator.generate_error_mail(target_node, str(e))

        generator.send_email(mail, node=target_node)
    generator.close_task()


class ReportSender:
    def __init__(self, report_task):
        self.report_task = report_task
        self.connection = get_connection()

    def _get_recipients(self, node=None):
        if not node:
            recipients = User.objects.filter(is_staff=True)
        else:
            recipients = node.admins.all()
        return [user.email for user in recipients if user.email]

    def send_email(self, mail, node=None):
        target = node.catalog_id if node else 'Red'
        mail.to = self._get_recipients(node=node)
        mail.connection = self.connection
        mail.from_email = DynamicEmailConfiguration.get_solo().from_email
        try:
            mail.send()
            msg = "Reporte de {} enviado exitosamente".format(target)
        except SMTPException as e:
            msg = "Error enviando reporte de {}:\n {}".format(target, str(e))
        self.report_task.info(self.report_task, msg)

    def close_connection(self):
        self.connection.close()


class EmailRenderer:

    def __init__(self, template_dir, txt_template, html_template,
                 error_dir=None):
        self.txt_template = os.path.join(template_dir, txt_template)
        self.html_template = os.path.join(template_dir, html_template)
        if error_dir:
            self.error_txt_template = os.path.join(error_dir, txt_template)
            self.error_html_template = os.path.join(error_dir, html_template)
        else:
            self.error_txt_template = self.error_html_template = None

    def render_templates(self, context):
        return self._render(self.txt_template, self.html_template, context)

    def render_error_templates(self, context):
        assert self.error_txt_template is not None
        assert self.error_html_template is not None
        return self._render(self.error_html_template, self.error_txt_template,
                            context)

    def _render(self, txt_template, html_template, context):
        msg = render_to_string(txt_template, context=context)
        html_msg = render_to_string(html_template, context=context)
        mail = EmailMultiAlternatives(body=msg,
                                      from_email=settings.EMAIL_HOST_USER)
        mail.attach_alternative(html_msg, 'text/html')
        return mail


class AbstractReportGenerator:
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, report_task, renderer):
        self.report_task = report_task
        self.sender = ReportSender(report_task)
        self.renderer = renderer

    def generate_email(self, node=None):
        raise NotImplementedError

    def close_task(self):
        self.sender.close_connection()
        self.report_task.refresh_from_db()
        self.report_task.status = self.report_task.FINISHED
        self.report_task.finished = timezone.now()
        self.report_task.save()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    def send_email(self, mail, node=None):
        self.sender.send_email(mail, node=node)

    def render_templates(self, context):
        return self.renderer.render_templates(context)

    def render_error_templates(self, context):
        return self.renderer.render_error_templates(context)


class IndicatorReportGenerator(AbstractReportGenerator):

    def __init__(self, indicators_task, report_task):
        self.indicators_task = indicators_task
        renderer = EmailRenderer('reports', 'indicators.txt', 'indicators.html')
        super(IndicatorReportGenerator, self).__init__(report_task, renderer)

    def generate_email(self, node=None):
        """Genera y manda el mail con el reporte de indexación. Si node es
        especificado, genera el reporte con valores de entidades pertenecientes
        únicamente a ese nodo (reporte individual). Caso contrario (default),
        genera el reporte de indexación global
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

        if not node:
            context['logs'] = self.indicators_task.logs

        start_time = self._format_date(self.indicators_task.created)
        subject = u'[{}] Indicadores Monitoreo Apertura: {}'.format(settings.ENV_TYPE, start_time)
        mail = self.render_templates(context)
        mail.subject = subject

        listed = context['listed']
        if not node:
            mail.attach('info.log', self.indicators_task.logs, 'text/plain')
        for indicator in listed:
            if listed[indicator]:
                body = render_to_string(
                    'reports/datasets.csv',
                    context={'dataset_list': listed[indicator]})
                mail.attach('{}.csv'.format(indicator), body, 'text/csv')
        return mail

    def _get_current_indicators(self, queryset, node=None):
        return queryset.sorted_indicators_on_date(
            self.indicators_task.finished.astimezone(
                timezone.get_current_timezone()).date(),
            node)


class ValidationReportGenerator(AbstractReportGenerator):
    def __init__(self, report_task):
        self.report_task = report_task
        renderer = EmailRenderer('reports', 'validation.txt', 'validation.html',
                                 error_dir='errors')
        super(ValidationReportGenerator, self).__init__(report_task, renderer)

    def generate_email(self, node=None):
        if not node:
            # No genera mail de staff
            return None
        catalog = DataJson(node.catalog_url)
        validation = catalog.validate_catalog(only_errors=True)
        validation_time = self._format_date(timezone.now())
        if validation['status'] == 'OK':
            msg = "Catálogo {} válido.".format(node.catalog_id)
            self.report_task.info(self.report_task, msg)
            return None
        context = {
            'validation_time': validation_time,
            'status': validation['status'],
            'catalog': validation['error']['catalog'],
            'dataset_list': validation['error']['dataset']
        }

        mail = self.render_templates(context)
        subject = u'[{}] Validacion de catálogo {}: {}'.format(
            settings.ENV_TYPE, node.catalog_id, validation_time)
        mail.subject = subject

        with NamedTemporaryFile(suffix='.xlsx') as tmpfile:
            catalog.validate_catalog(export_path=tmpfile.name)
            mail.attach('reporte_validacion_{}.xlsx'.format(node.catalog_id),
                        tmpfile.read())

        return mail

    def generate_error_mail(self, node, error):
        context = {'error': error}
        validation_time = self._format_date(timezone.now())
        mail = self.render_error_templates(context)
        subject = u'[{}] Error validando catálogo {}: {}'.format(
            settings.ENV_TYPE, node.catalog_id, validation_time)
        mail.subject = subject
        return mail

    def send_email(self, mail, node=None):
        # Si mail es None, la validación no encontró errores.
        # No hay nada que mandar
        if mail is not None:
            super(ValidationReportGenerator, self).send_email(mail, node=node)

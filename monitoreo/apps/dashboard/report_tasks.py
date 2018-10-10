# coding=utf-8
from __future__ import unicode_literals

from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django_rq import job

from django_datajsonar.models import Node

from .models import Indicador, IndicadorRed, IndicatorType,\
    IndicatorsGenerationTask, ReportGenerationTask


@job('reports')
def send_reports(report_task=None):
    try:
        indicators_task = IndicatorsGenerationTask.objects\
            .filter(status=IndicatorsGenerationTask.FINISHED).latest('finished')
    except IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return

    report_task = report_task or ReportGenerationTask.objects.create()

    generator = ReportGenerator(indicators_task, report_task)
    generator.generate_email()

    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        generator.generate_email(node)

    generator.close_task()


class ReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, indicators_task, report_task):
        self.indicators_task = indicators_task
        self.report_task = report_task

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
                sorted_indicators_on_date(self.indicators_task.finished.date())
            one_dimensional, multi_dimensional, listed = \
                IndicadorRed.objects.filter(indicador_tipo__mostrar=True).\
                sorted_indicators_on_date(self.indicators_task.finished.date())
            target = 'Red'
        else:
            one_d_summary, multi_d_summary, _ = \
                Indicador.objects.filter(indicador_tipo__resumen=True).\
                sorted_indicators_on_date(self.indicators_task.finished.date(), node)
            one_dimensional, multi_dimensional, listed = \
                Indicador.objects.filter(indicador_tipo__mostrar=True)\
                .sorted_indicators_on_date(self.indicators_task.finished.date(), node)
            target = node.catalog_id

        context.update({
            'target': target,
            'one_d_summary': one_d_summary,
            'multi_d_summary': multi_d_summary,
            'one_dimensional_indics': one_dimensional,
            'multi_dimensional_indics': multi_dimensional,
        })
        self.send_email(context, listed, node)

    def send_email(self, context, listed, node=None):
        if not node:
            recipients = User.objects.filter(is_staff=True)
        else:
            recipients = node.admins.all()

        emails = [user.email for user in recipients if user.email]

        if not emails:  # Nothing to do here
            return

        start_time = self._format_date(self.indicators_task.created)
        subject = u'[{}] Indicadores Monitoreo Apertura: {}'.format(settings.ENV_TYPE, start_time)

        msg = render_to_string('reports/report.txt', context=context)
        mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER, emails)
        html_msg = render_to_string('reports/report.html', context=context)
        mail.attach_alternative(html_msg, 'text/html')

        if not node:
            mail.attach('info.log', self.indicators_task.logs, 'text/plain')

        for indicator in listed:
            if listed[indicator]:
                body = render_to_string('reports/datasets.csv', context={'dataset_list': listed[indicator]})
                mail.attach('{}.csv'.format(indicator), body, 'text/csv')

        try:
            mail.send()
            msg = "Reporte de {} enviado exitosamente".format(context['target'])
        except SMTPException as e:
            msg = "Error enviando reporte de {}:\n {}".format(context['target'], str(e))

        ReportGenerationTask.info(self.report_task, msg)

    def close_task(self):
        self.report_task.refresh_from_db()
        self.report_task.status = ReportGenerationTask.FINISHED
        self.report_task.finished = timezone.now()
        self.report_task.save()

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

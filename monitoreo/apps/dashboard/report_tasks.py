# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from django_datajsonar.models import Node

from .models import Indicador, IndicadorRed, IndicatorsGenerationTask


def send_reports():
    try:
        task = IndicatorsGenerationTask.objects\
            .filter(status=IndicatorsGenerationTask.FINISHED).latest('finished')
    except IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return
    generator = ReportGenerator(task)
    generator.generate_email()

    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        generator.generate_email(node)


class ReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, task):
        self.task = task

    def generate_email(self, node=None):
        """Genera y manda el mail con el reporte de indexación. Si node es especificado, genera el reporte
        con valores de entidades pertenecientes únicamente a ese nodo (reporte individual). Caso contrario
        (default), genera el reporte de indexación global
        """

        context = {
            'finish_time': self._format_date(self.task.finished)
        }
        if not node:
            one_dimensional, multi_dimensional, listed = \
                IndicadorRed.objects.sorted_indicators_on_date(self.task.finished.date())
            target = 'Red'
        else:
            one_dimensional, multi_dimensional, listed = \
                Indicador.objects.sorted_indicators_on_date(self.task.finished.date(), node)
            target = node.catalog_id

        context.update({
            'target': target,
            'one_dimensional_indics': one_dimensional,
            'multi_dimensional_indics': multi_dimensional
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

        start_time = self._format_date(self.task.created)
        subject = u'[{}] Indicadores Monitoreo Apertura: {}'.format(settings.ENV_TYPE, start_time)

        msg = render_to_string('reports/report.txt', context=context)
        mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER, emails)
        html_msg = render_to_string('reports/report.html', context=context)
        mail.attach_alternative(html_msg, 'text/html')

        if not node:
            mail.attach('info.log', self.task.logs, 'text/plain')

        for indicator in listed:
            if listed[indicator]:
                body = render_to_string('reports/datasets.csv', context={'dataset_list': listed[indicator]})
                mail.attach('{}.csv'.format(indicator), body, 'text/csv')

        sent = mail.send()
        if emails and not sent:
            raise ValueError

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

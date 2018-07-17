# coding=utf-8
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import IndicadorRed, IndicatorsGenerationTask


def send_staff_report():
    try:
        task = IndicatorsGenerationTask.objects.latest('finished')
    except IndicatorsGenerationTask.DoesNotExist:
        # No hay un task cargado
        return
    generator = ReportGenerator(task)
    generator.generate_email()


class ReportGenerator(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, task):
        self.task = task

    def generate_email(self):
        """Genera y manda el mail con el reporte de indexación. Si node es especificado, genera el reporte
        con valores de entidades pertenecientes únicamente a ese nodo (reporte individual). Caso contrario
        (default), genera el reporte de indexación global
        """

        context = {
            'finish_time': self._format_date(self.task.finished)
        }
        latest_indicators = IndicadorRed.objects.filter(fecha=self.task.finished.date())
        one_dimensional, multi_dimensional, listed = self._sort_indicators(latest_indicators)
        context.update({
            'one_dimensional_indics': one_dimensional,
            'multi_dimensional_indics': multi_dimensional
        })
        self.send_email(context, listed)

    def send_email(self, context, listed):

        recipients = User.objects.filter(is_staff=True)
        emails = [user.email for user in recipients]

        if not emails:  # Nothing to do here
            return

        start_time = self._format_date(self.task.created)
        subject = u'Indicadores Monitoreo Apertura: {}'.format(start_time)

        msg = render_to_string('reports/report.txt', context=context)
        mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER, emails)
        html_msg = render_to_string('reports/report.html', context=context)
        mail.attach_alternative(html_msg, 'text/html')

        mail.attach('info.log', self.task.logs, 'text/plain')
        for indicator in listed:
            body = render_to_string('reports/datasets.csv', context={'dataset_list': listed[indicator]})
            mail.attach('{}.csv'.format(indicator), body, 'text/csv')

        sent = mail.send()
        if emails and not sent:
            raise ValueError

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)

    @staticmethod
    def _sort_indicators(queryset):
        one_dimensional = {}
        multi_dimensional = {}
        listed = {}
        for indicator in queryset:
            value = json.loads(indicator.indicador_valor)
            if isinstance(value, dict):
                multi_dimensional[indicator.indicador_tipo.nombre] = value
            elif isinstance(value, list):
                listed[indicator.indicador_tipo.nombre] = value
            else:
                one_dimensional[indicator.indicador_tipo.nombre] = value

        return one_dimensional, multi_dimensional, listed

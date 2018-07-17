# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import IndicadorRed


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
        indicator_dict = {indicator.indicador_tipo.nombre: indicator.indicador_valor for indicator in latest_indicators}
        context.update({
            'latest_indicators': indicator_dict
        })
        self.send_email(context)

    def send_email(self, context):

        recipients = User.objects.filter(is_staff=True)
        emails = [user.email for user in recipients]

        if not emails:  # Nothing to do here
            return

        start_time = self._format_date(self.task.created)
        subject = u'[{}] Monitoreo Apertura: {}'.format(settings.ENV_TYPE, start_time)

        msg = render_to_string('reports/report.txt', context=context)
        mail = EmailMultiAlternatives(subject, msg, settings.EMAIL_HOST_USER, emails)
        html_msg = render_to_string('reports/report.html', context=context)
        mail.attach_alternative(html_msg, 'text/html')

        mail.attach('errors.log', self.task.logs, 'text/plain')

        sent = mail.send()
        if emails and not sent:
            raise ValueError

    def _format_date(self, date):
        return timezone.localtime(date).strftime(self.DATE_FORMAT)
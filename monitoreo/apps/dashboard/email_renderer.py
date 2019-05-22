# coding=utf-8
from __future__ import unicode_literals

import os
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from des.models import DynamicEmailConfiguration


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

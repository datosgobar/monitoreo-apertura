#! coding: utf-8
from __future__ import unicode_literals
import os

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import TestCase

from monitoreo.apps.dashboard.models import IndicatorsGenerationTask, IndicatorType, IndicadorRed
from monitoreo.apps.dashboard.report_tasks import ReportGenerator

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class ReportGenerationTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):

        # set mock env
        settings.ENV_TYPE = 'tst'

        # set mock user
        cls.staff_user = User(username='staff', password='staff', email='staff@test.com', is_staff=True)
        cls.staff_user.save()
        cls.regular_user = User(username='regular', password='regular', email='regular@test.com', is_staff=False)
        cls.regular_user.save()

        # set mock task
        cls.task = IndicatorsGenerationTask(
            status=IndicatorsGenerationTask.FINISHED,
            finished=timezone.now(),
            logs='test task logs'
        )

        # set mock indicators
        type_a = IndicatorType(nombre='ind_a', tipo='RED')
        type_a.save()
        type_b = IndicatorType(nombre='ind_b', tipo='RED')
        type_b.save()
        type_c = IndicatorType(nombre='ind_c', tipo='RED')
        type_c.save()

        ind_a = IndicadorRed(indicador_tipo=type_a, indicador_valor='42')
        ind_a.save()
        ind_b = IndicadorRed(indicador_tipo=type_b, indicador_valor='[["d1", "l1"], ["d2", "l2"]]')
        ind_b.save()
        ind_c = IndicadorRed(indicador_tipo=type_c, indicador_valor='{"k1": 1, "k2": 2}')
        ind_c.save()

        cls.report_generator = ReportGenerator(cls.task)

    def setUp(self):
        self.report_generator.generate_email()
        self.mail = mail.outbox[0]

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_staff_members(self):
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(['staff@test.com'], self.mail.to)

    def test_subject(self):
        start_time = timezone.localtime(self.task.created).strftime('%Y-%m-%d %H:%M:%S')
        subject = u'[tst] Indicadores Monitoreo Apertura: {}'.format(start_time)
        self.assertEqual(subject, self.mail.subject)

    def test_mail_body(self):
        body = self.mail.body
        self.assertTrue('ind_a: 42' in body)
        self.assertTrue('ind_c:\n' in body)
        self.assertTrue('k1: 1' in body)
        self.assertTrue('k2: 2' in body)

    def test_info_attachment(self):
        self.assertTrue(('info.log', 'test task logs', 'text/plain') in self.mail.attachments)

    def test_list_attachment(self):
        self.assertTrue(('ind_b.csv', 'dataset_title,landing_page\nd1, l1\nd2, l2\n', 'text/csv') in
                        self.mail.attachments)



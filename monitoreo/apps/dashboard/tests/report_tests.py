#! coding: utf-8
from __future__ import unicode_literals
import os

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.core import mail
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

    def setUp(self):
        # set mock user
        self.staff_user = User(username='staff', password='staff', email='staff@test.com', is_staff=True)
        self.staff_user.save()
        self.regular_user = User(username='regular', password='regular', email='regular@test.com', is_staff=False)
        self.regular_user.save()

        # set mock task
        self.task = IndicatorsGenerationTask(
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
        ind_b = IndicadorRed(indicador_tipo=type_b, indicador_valor='[("d1", "l1"), ("d2","l2")]')
        ind_b.save()
        ind_c = IndicadorRed(indicador_tipo=type_c, indicador_valor='{"k1": 1, "k2": 2}')
        ind_c.save()

        self.report_generator = ReportGenerator(self.task)

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_staff_members(self):
        pass

    def test_info_attachment(self):
        pass

    def test_list_attachment(self):
        pass

    def test_mail_body(self):
        pass

    def test_subject(self):
        pass

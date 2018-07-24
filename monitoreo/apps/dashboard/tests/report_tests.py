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

from django_datajsonar.models import Node

from monitoreo.apps.dashboard.models import ReportGenerationTask, IndicatorsGenerationTask,\
    IndicatorType, IndicadorRed, Indicador
from monitoreo.apps.dashboard.report_tasks import ReportGenerator, send_reports

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
        User.objects.create(username='staff', password='staff', email='staff@test.com', is_staff=True)

        # set mock nodes
        cls.node1 = Node.objects.create(catalog_id='id1', catalog_url='url', indexable=True)
        cls.node2 = Node.objects.create(catalog_id='id2', catalog_url='url', indexable=True)

        cls.node1.admins.create(username='admin1', password='regular', email='admin1@test.com', is_staff=False)
        cls.node2.admins.create(username='admin2', password='regular', email='admin2@test.com', is_staff=False)

        # set mock task
        cls.indicators_task = IndicatorsGenerationTask.objects.create(
            finished=timezone.now(),
            logs='test task logs'
        )
        cls.indicators_task.status = IndicatorsGenerationTask.FINISHED
        cls.indicators_task.save()

        cls.report_task = ReportGenerationTask.objects.create()

        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED')

        types = [type_a, type_b, type_c]
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}']
        for t, v in zip(types, values):
            IndicadorRed.objects.create(indicador_tipo=t, indicador_valor=v)
        values = ['23', '[["d1", "l1"]]', '{"k2": 1}']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='id1',
                                     jurisdiccion_nombre='nodo1')
        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='id2',
                                     jurisdiccion_nombre='nodo2')
        cls.report_generator = ReportGenerator(cls.indicators_task, cls.report_task)

    def setUp(self):
        self.report_generator.generate_email()
        self.mail = mail.outbox[0]

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_staff_members(self):
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(['staff@test.com'], self.mail.to)

    def test_subject(self):
        start_time = timezone.localtime(self.indicators_task.created).strftime('%Y-%m-%d %H:%M:%S')
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

    def test_nodes_email_outbox(self):
        mail.outbox = []
        self.report_generator.generate_email(node=self.node2)
        self.assertEqual(1, len(mail.outbox))
        sent_mail = mail.outbox[0]
        self.assertEqual(['admin2@test.com'], sent_mail.to)
        self.assertTrue('ind_a: 19' in sent_mail.body)
        self.assertTrue(1, len(sent_mail.attachments))
        self.assertTrue(('ind_b.csv', 'dataset_title,landing_page\nd2, l2\n', 'text/csv') in
                        sent_mail.attachments)

    def test_task_is_closed(self):
        self.report_generator.close_task()
        self.assertEqual(ReportGenerationTask.FINISHED, self.report_generator.report_task.status)

    def test_send_report(self):
        mail.outbox = []
        send_reports()
        self.assertEqual(3, len(mail.outbox))

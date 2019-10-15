#! coding: utf-8
from __future__ import unicode_literals

import os
import re

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import TestCase
from des.models import DynamicEmailConfiguration

from django_datajsonar.models import Node

from monitoreo.apps.dashboard.models.tasks import \
    ReportGenerationTask, IndicatorsGenerationTask
from monitoreo.apps.dashboard.models.indicators import \
    IndicatorType, IndicadorRed, Indicador, IndicadorFederador
from monitoreo.apps.dashboard.models.nodes import \
    HarvestingNode, CentralNode
from monitoreo.apps.dashboard.report_tasks import \
    IndicatorReportGenerator, send_reports

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class IndicatorReportGenerationTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

        config = DynamicEmailConfiguration.get_solo()
        config.from_email = 'from_test@test.com'
        config.save()

        # set mock task
        cls.indicators_task = IndicatorsGenerationTask.objects.create(finished=timezone.now(), logs='test task logs')
        cls.indicators_task.status = IndicatorsGenerationTask.FINISHED
        cls.indicators_task.save()

        # set mock user
        User.objects.create(username='staff', password='staff', email='staff@test.com', is_staff=True)

        # set mock nodes
        cls.node1 = Node.objects.create(catalog_id='id1', catalog_url='url', indexable=True)
        cls.node2 = Node.objects.create(catalog_id='id2', catalog_url='url', indexable=True)

        cls.node1.admins.create(username='admin1', password='regular', email='admin1@test.com', is_staff=False)
        cls.node2.admins.create(username='admin2', password='regular', email='admin2@test.com', is_staff=False)

        cls.harvest_node = HarvestingNode.objects.create(catalog_id='harvest_id', name='harvest node',
                                                         url='http://datos.test.ar', apikey='apikey', enabled=True)
        central_node = CentralNode.get_solo()
        central_node.node = cls.harvest_node
        central_node.save()

        cls.report_task = ReportGenerationTask.objects.create()

        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED', resumen=True)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED', resumen=True, mostrar=False)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED', mostrar=False)

        types = [type_a, type_b, type_c, type_d, type_e]
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}', '100', '1']
        for t, v in zip(types, values):
            IndicadorRed.objects.create(indicador_tipo=t, indicador_valor=v)
        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='id1',
                                     jurisdiccion_nombre='nodo1')
        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='id2',
                                     jurisdiccion_nombre='nodo2')

        values = ['23', '[["d2", "l2"]]', '{"k2": 1}', '2', '3']
        for t, v in zip(types, values):
            IndicadorFederador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='harvest_id',
                                              jurisdiccion_nombre='harvest node')
        cls.indicators_report_generator = IndicatorReportGenerator(cls.indicators_task, cls.report_task)

    def setUp(self):
        email = self.indicators_report_generator\
            .generate_network_indicators_email()
        self.indicators_report_generator.send_email(email)
        self.mail = mail.outbox[0]

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_staff_members(self):
        self.assertEqual(1, len(mail.outbox))
        self.assertIn('staff@test.com', self.mail.to)

    def test_mail_uses_des_from(self):
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual('from_test@test.com', self.mail.from_email)

    def test_subject(self):
        start_time = timezone.localtime(self.indicators_task.created).strftime('%Y-%m-%d %H:%M:%S')
        subject = '[tst] Indicadores Monitoreo Apertura (Red): {}'.format(start_time)
        self.assertEqual(subject, self.mail.subject)

    def test_mail_header(self):
        header, _, _ = filter(None, re.split(r'Resumen:|Detalle:', self.mail.body))
        finish_time = timezone.localtime(self.indicators_task.finished)\
            .strftime('%Y-%m-%d %H:%M:%S')
        expected_header = 'Horario de finalización: {}\n\ntest task logs\n\n'\
            .format(finish_time)
        self.assertEqual(expected_header, header)

    def test_mail_summary(self):
        _, summary, detail = filter(None, re.split(r'Resumen:|Detalle:', self.mail.body))
        self.assertIn('ind_d: 100', summary)
        self.assertIn('ind_c:\n', summary)
        self.assertIn('k1: 1', summary)
        self.assertIn('k2: 2', summary)
        self.assertNotIn('ind_a', summary)
        self.assertNotIn('ind_d', detail)
        self.assertIn('ind_c', detail)

    def test_mail_detail(self):
        _, summary, detail = filter(None, re.split(r'Resumen:|Detalle:', self.mail.body))
        self.assertIn('ind_a: 42', detail)
        self.assertIn('ind_c:\n', detail)
        self.assertIn('k1: 1', detail)
        self.assertIn('k2: 2', detail)
        self.assertNotIn('ind_d', detail)
        self.assertNotIn('ind_a', summary)
        self.assertIn('ind_c', summary)

    def test_info_attachment(self):
        self.assertIn(('info.log', 'test task logs', 'text/plain'),
                      self.mail.attachments)

    def test_list_attachment(self):
        self.assertIn(('ind_b.csv', 'dataset_title,landing_page\nd1, l1\nd2, l2\n', 'text/csv'),
                      self.mail.attachments)

    def test_nodes_email_outbox(self):
        mail.outbox = []
        email = self.indicators_report_generator.\
            generate_node_indicators_email(node=self.node2)
        self.indicators_report_generator.send_email(email, node=self.node2)
        self.assertEqual(1, len(mail.outbox))
        sent_mail = mail.outbox[0]
        self.assertIn('admin2@test.com', sent_mail.to)
        self.assertIn('ind_a: 19', sent_mail.body)
        self.assertEqual(1, len(sent_mail.attachments))
        self.assertIn(('ind_b.csv', 'dataset_title,landing_page\nd2, l2\n', 'text/csv'),
                      sent_mail.attachments)

    def test_task_log(self):
        email = self.indicators_report_generator.\
            generate_node_indicators_email(node=self.node2)
        self.indicators_report_generator.send_email(email, node=self.node2)
        staff_mail = mail.outbox[0]
        node_mail = mail.outbox[1]
        self.assertIn('test task logs', staff_mail.body)
        self.assertNotIn('test task logs', node_mail.body)

    def test_task_is_closed(self):
        self.indicators_report_generator.close_task()
        self.assertEqual(ReportGenerationTask.FINISHED,
                         self.indicators_report_generator.report_task.status)

    def test_send_report(self):
        mail.outbox = []
        send_reports()
        # Red, nodo central y 2 de nodos
        self.assertEqual(4, len(mail.outbox))

    def test_send_central_node_indicators(self):
        mail.outbox = []
        central_node = CentralNode.get_solo().node
        email = self.indicators_report_generator. \
            generate_federation_indicators_email(central_node)
        self.indicators_report_generator.send_email(email)
        self.assertEqual(1, len(mail.outbox))
        sent_mail = mail.outbox[0]
        self.assertIn('staff@test.com', sent_mail.to)
        self.assertIn('ind_a: 23', sent_mail.body)
        self.assertTrue(1, len(sent_mail.attachments))
        self.assertIn(
            ('ind_b.csv', 'dataset_title,landing_page\nd2, l2\n', 'text/csv'),
            sent_mail.attachments)

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
from django.utils.html import escape
from django.test import TestCase

from django_datajsonar.models import Node
from pydatajson.core import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog

from monitoreo.apps.dashboard.models import ReportGenerationTask, IndicatorsGenerationTask,\
    IndicatorType, IndicadorRed, Indicador, ValidationReportTask
from monitoreo.apps.dashboard.report_tasks import IndicatorReportGenerator, send_reports,\
    ValidationReportGenerator, send_validations

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class IndicatorReportGenerationTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

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
        cls.indicators_report_generator = IndicatorReportGenerator(cls.indicators_task, cls.report_task)

    def setUp(self):
        self.indicators_report_generator.send_email(self.indicators_report_generator.generate_email())
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

    def test_mail_header(self):
        header, _, _ = filter(None, re.split(r'Resumen:|Detalle:', self.mail.body))
        finish_time = timezone.localtime(self.indicators_task.finished)\
            .strftime('%Y-%m-%d %H:%M:%S')
        expected_header = 'Horario de finalización: {}\n\ntest task logs\n\n'\
            .format(finish_time)
        self.assertEqual(expected_header, header)

    def test_mail_summary(self):
        _, summary, detail = filter(None, re.split(r'Resumen:|Detalle:', self.mail.body))
        self.assertTrue('ind_d: 100' in summary)
        self.assertTrue('ind_c:\n' in summary)
        self.assertTrue('k1: 1' in summary)
        self.assertTrue('k2: 2' in summary)
        self.assertTrue('ind_a' not in summary)
        self.assertTrue('ind_d' not in detail)
        self.assertTrue('ind_c' in detail)

    def test_mail_detail(self):
        _, summary, detail = filter(None, re.split(r'Resumen:|Detalle:', self.mail.body))
        self.assertTrue('ind_a: 42' in detail)
        self.assertTrue('ind_c:\n' in detail)
        self.assertTrue('k1: 1' in detail)
        self.assertTrue('k2: 2' in detail)
        self.assertTrue('ind_d' not in detail)
        self.assertTrue('ind_a' not in summary)
        self.assertTrue('ind_c' in summary)

    def test_info_attachment(self):
        self.assertTrue(('info.log', 'test task logs', 'text/plain') in self.mail.attachments)

    def test_list_attachment(self):
        self.assertTrue(('ind_b.csv', 'dataset_title,landing_page\nd1, l1\nd2, l2\n', 'text/csv') in
                        self.mail.attachments)

    def test_nodes_email_outbox(self):
        mail.outbox = []
        self.indicators_report_generator.send_email(self.indicators_report_generator.generate_email(node=self.node2), node=self.node2)
        self.assertEqual(1, len(mail.outbox))
        sent_mail = mail.outbox[0]
        self.assertEqual(['admin2@test.com'], sent_mail.to)
        self.assertTrue('ind_a: 19' in sent_mail.body)
        self.assertTrue(1, len(sent_mail.attachments))
        self.assertTrue(('ind_b.csv', 'dataset_title,landing_page\nd2, l2\n', 'text/csv') in
                        sent_mail.attachments)

    def test_task_log(self):
        self.indicators_report_generator.send_email(self.indicators_report_generator.generate_email(node=self.node2), node=self.node2)
        staff_mail = mail.outbox[0]
        node_mail = mail.outbox[1]
        self.assertTrue('test task logs' in staff_mail.body)
        self.assertFalse('test task logs' in node_mail.body)

    def test_task_is_closed(self):
        self.indicators_report_generator.close_task()
        self.assertEqual(ReportGenerationTask.FINISHED, self.indicators_report_generator.report_task.status)

    def test_send_report(self):
        mail.outbox = []
        send_reports()
        self.assertEqual(3, len(mail.outbox))


class ValidationReportGenerationTest(TestCase):
    NOW_FOR_TESTING = timezone.datetime(2010, 10, 10, 10, tzinfo=timezone.utc)

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

        # set mock nodes
        cls.node1 = Node.objects.create(catalog_id='id1', catalog_url=cls.get_sample('several_assorted_errors.json'), indexable=True)
        cls.node2 = Node.objects.create(catalog_id='id2', catalog_url=cls.get_sample('full_data.json'), indexable=True)

        cls.node1.admins.create(username='admin1', password='regular', email='admin1@test.com', is_staff=False)
        cls.node2.admins.create(username='admin2', password='regular', email='admin2@test.com', is_staff=False)

        cls.report_task = ValidationReportTask.objects.create()

        cls.validation_report_generator = ValidationReportGenerator(cls.report_task)

        catalog = DataJson(cls.get_sample('several_assorted_errors.json'))
        cls.report = catalog.validate_catalog(only_errors=True)

    def setUp(self):
        with patch('django.utils.timezone.now', return_value=self.NOW_FOR_TESTING):
            self.validation_report_generator.send_email(
                self.validation_report_generator.generate_email(self.node1),
                node=self.node1)
            self.mail = mail.outbox[0]

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_node_admin(self):
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(['admin1@test.com'], self.mail.to)

    def test_subject(self):
        subject = u'[tst] Validacion de catálogo id1: 2010-10-10 07:00:00'
        self.assertEqual(subject, self.mail.subject)

    def test_mail_header(self):
        header, _, _ = filter(None, re.split(r'Validación datos de catálogo:|Validacion datos de datasets:', self.mail.body))
        expected_header = 'Horario de inspección:'
        self.assertTrue(header.startswith(expected_header))

    def test_catalog_validation(self):
        _, catalog_validation, dataset_validation =\
            filter(None, re.split(r'Validación datos de catálogo:|Validacion datos de datasets:', self.mail.body))
        for error in self.report['error']['catalog']['errors']:
            self.assertTrue(escape(error['message']) in catalog_validation)

    def test_dataset_validation(self):
        _, catalog_validation, dataset_validation =\
            filter(None, re.split(r'Validación datos de catálogo:|Validacion datos de datasets:', self.mail.body))
        for error in self.report['error']['dataset'][0]['errors']:
            self.assertTrue(escape(error['message']) in dataset_validation)

    def test_mail_attachment(self):
        attachments = [attachment[0] for attachment in self.mail.attachments]
        self.assertTrue('reporte_validacion_id1.xlsx' in attachments)

    def test_valid_node_does_not_trigger_email(self):
        valid_node_mail = self.validation_report_generator.generate_email(node=self.node2)
        self.assertIsNone(valid_node_mail)

    def test_task_is_closed(self):
        self.validation_report_generator.close_task()
        self.assertEqual(ValidationReportTask.FINISHED,
                         self.validation_report_generator.report_task.status)

    def test_send_report(self):
        mail.outbox = []
        send_validations()
        self.assertEqual(1, len(mail.outbox))

    def test_send_error_mail(self):
        def mock_side_effect(catalog):
            raise NonParseableCatalog(catalog, 'Test Error')

        mail.outbox = []
        with patch('monitoreo.apps.dashboard.report_tasks.DataJson',
                   side_effect=mock_side_effect):
            send_validations()

        expected_header = 'Ocurrió un error intentando acceder al catálogo:'
        expected_error = 'Test Error'
        error_mail = mail.outbox[0]
        self.assertEqual(2, len(mail.outbox))
        self.assertTrue(expected_header in error_mail.body)
        self.assertTrue(expected_error in error_mail.body)

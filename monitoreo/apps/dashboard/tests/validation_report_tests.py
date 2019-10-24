#! coding: utf-8
from __future__ import unicode_literals

import os
import re

from monitoreo.apps.dashboard.models.tasks import TasksConfig

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.utils.html import escape
from django.test import TestCase
from des.models import DynamicEmailConfiguration

from django_datajsonar.models import Node
from pydatajson.core import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog

from monitoreo.apps.dashboard.models import ValidationReportTask
from monitoreo.apps.dashboard.report_tasks import ValidationReportGenerator, send_validations

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class ValidationReportGenerationTest(TestCase):
    NOW_FOR_TESTING = timezone.datetime(2010, 10, 10, 10, tzinfo=timezone.utc)

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
        subject = '[tst] Validacion de catálogo id1: 2010-10-10 07:00:00'
        self.assertEqual(subject, self.mail.subject)

    def test_mail_uses_des_from(self):
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual('from_test@test.com', self.mail.from_email)

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

        dataset_errors = list(self.report['error']['dataset'])
        for error in dataset_errors[0]['errors']:
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
        def mock_side_effect(catalog, catalog_format=None):
            raise NonParseableCatalog(catalog, 'Test Error')

        mail.outbox = []
        with patch('monitoreo.apps.dashboard.report_generators.DataJson',
                   side_effect=mock_side_effect):
            send_validations()

        expected_header = 'Ocurrió un error intentando acceder al catálogo:'
        expected_error = 'Test Error'
        error_mail = mail.outbox[0]
        self.assertEqual(2, len(mail.outbox))
        self.assertTrue(expected_header in error_mail.body)
        self.assertTrue(expected_error in error_mail.body)

    def test_reports_not_validated_with_url_if_flag_is_false(self):
        TasksConfig.objects.update(validation_url_check=False)

        with patch('monitoreo.apps.dashboard.report_generators.DataJson.validate_catalog') as m:
            send_validations()

        broken_links_call_value = m.call_args_list[0][1]['broken_links']
        self.assertFalse(broken_links_call_value)

    def test_reports_validated_with_url_by_default(self):
        with patch('monitoreo.apps.dashboard.report_generators.DataJson.validate_catalog') as m:
            send_validations()

        broken_links_call_value = m.call_args_list[0][1]['broken_links']
        self.assertTrue(broken_links_call_value)

    def test_reports_not_validated_with_url_if_node_flag_is_false(self):
        Node.objects.update(validate_catalog_urls=False)
        with patch('monitoreo.apps.dashboard.report_generators.DataJson.validate_catalog') as m:
            send_validations()

        broken_links_call_value = m.call_args_list[0][1]['broken_links']
        self.assertFalse(broken_links_call_value)

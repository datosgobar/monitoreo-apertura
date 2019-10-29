from __future__ import unicode_literals

import os

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django_datajsonar.models import Node, Catalog, Dataset

from monitoreo.apps.dashboard.models.dataset_present_record import DatasetPresentRecord
from monitoreo.apps.dashboard.models.tasks import NotPresentReportGenerationTask
from monitoreo.apps.dashboard.report_generators import NotPresentReportGenerator
from monitoreo.apps.dashboard.report_tasks import send_not_present_reports

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.test import TestCase
from des.models import DynamicEmailConfiguration

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class NotPresentDatasetReportGenerationTest(TestCase):

    NOW_FOR_TESTING = timezone.datetime(2018, 10, 10, 10, tzinfo=timezone.utc)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

        config = DynamicEmailConfiguration.get_solo()
        config.from_email = 'from_test@test.com'
        config.save()

        # set mock nodes
        cls.node1 = Node.objects.create(catalog_id='id1', catalog_url='url', indexable=True)
        cls.node2 = Node.objects.create(catalog_id='id2', catalog_url='url', indexable=True)
        cls.node3 = Node.objects.create(catalog_id='id3', catalog_url='url', indexable=True)
        cls.node4 = Node.objects.create(catalog_id='id4', catalog_url='url', indexable=True)
        cls.node5 = Node.objects.create(catalog_id='id5', catalog_url='url', indexable=True)
        cls.node6 = Node.objects.create(catalog_id='id6', catalog_url='url', indexable=True)

        cls.node1.admins.create(username='admin1', password='regular', email='admin1@test.com',
                                is_staff=False)
        cls.node2.admins.create(username='admin2', password='regular', email='admin2@test.com',
                                is_staff=False)
        cls.node3.admins.create(username='admin3', password='regular', email='admin3@test.com',
                                is_staff=False)
        cls.node4.admins.create(username='admin4', password='regular', email='admin4@test.com',
                                is_staff=False)
        cls.node5.admins.create(username='admin5', password='regular', email='admin5@test.com',
                                is_staff=False)
        cls.node6.admins.create(username='admin6', password='regular', email='admin6@test.com',
                                is_staff=False)

        # set mock user
        User.objects.create(username='staff', password='staff', email='staff@test.com',
                            is_staff=True)

        cls.catalog1 = Catalog.objects.create(title='id1', identifier='id1')
        cls.catalog2 = Catalog.objects.create(title='id2', identifier='id2')
        cls.catalog3 = Catalog.objects.create(title='id3', identifier='id3')
        cls.catalog4 = Catalog.objects.create(title='id4', identifier='id4')
        cls.catalog5 = Catalog.objects.create(title='id5', identifier='id5')
        cls.catalog6 = Catalog.objects.create(title='id6', identifier='id6')

        cls.dataset1 = Dataset.objects.create(identifier='dataset1', metadata='{}',
                                              catalog=cls.catalog1, indexable=True, present=True, updated=True)
        cls.dataset2 = Dataset.objects.create(identifier='dataset2', metadata='{}',
                                              catalog=cls.catalog2, indexable=True, present=False, updated=True)
        cls.dataset3 = Dataset.objects.create(identifier='dataset3', metadata='{}',
                                              catalog=cls.catalog3, indexable=True, present=True, updated=True)
        cls.dataset4 = Dataset.objects.create(identifier='dataset4', metadata='{}',
                                              catalog=cls.catalog4, indexable=True, present=False, updated=True)
        cls.dataset5 = Dataset.objects.create(identifier='dataset5', metadata='{}',
                                              catalog=cls.catalog5, indexable=True, present=True, updated=True)
        cls.dataset6 = Dataset.objects.create(identifier='dataset6', metadata='{}',
                                              catalog=cls.catalog6, indexable=True, present=False, updated=True)

        # set mock dataset present record
        DatasetPresentRecord.objects.create(dataset_id=cls.dataset1.id, present_record=True)
        DatasetPresentRecord.objects.create(dataset_id=cls.dataset2.id, present_record=False)
        DatasetPresentRecord.objects.create(dataset_id=cls.dataset3.id, present_record=False)
        DatasetPresentRecord.objects.create(dataset_id=cls.dataset4.id, present_record=True)

        cls.not_present_report_task = NotPresentReportGenerationTask.objects.create()

        cls.not_present_report_generator = NotPresentReportGenerator(cls.not_present_report_task)

    def setUp(self):
        with patch('django.utils.timezone.now', return_value=self.NOW_FOR_TESTING):
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email(self.node1),
                node=self.node1)
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email(self.node2),
                node=self.node2)
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email(self.node3),
                node=self.node3)
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email(self.node4),
                node=self.node4)
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email(self.node5),
                node=self.node5)
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email(self.node6),
                node=self.node6)
            self.not_present_report_generator.send_email(
                self.not_present_report_generator.generate_email())
            self.node1_mail = mail.outbox[0]
            self.node2_mail = mail.outbox[1]
            self.node3_mail = mail.outbox[2]
            self.node4_mail = mail.outbox[3]
            self.node5_mail = mail.outbox[4]
            self.node6_mail = mail.outbox[5]
            self.staff_mail = mail.outbox[6]

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_only_node_admins(self):
        self.assertEqual(7, len(mail.outbox))
        self.assertEqual(['admin1@test.com'], self.node1_mail.to)
        self.assertEqual(['admin2@test.com'], self.node2_mail.to)
        self.assertEqual(['admin3@test.com'], self.node3_mail.to)
        self.assertEqual(['admin4@test.com'], self.node4_mail.to)
        self.assertEqual(['admin5@test.com'], self.node5_mail.to)
        self.assertEqual(['admin6@test.com'], self.node6_mail.to)

    def test_mail_is_sent_to_staff_members(self):
        self.assertEqual(['staff@test.com'], self.staff_mail.to)

    def test_subject_for_nodes(self):
        subject = '[tst] Reporte de datasets no presentes de Monitoreo Apertura para id1 del 2018-10-10'
        self.assertEqual(subject, self.node1_mail.subject)

    def test_subject_for_staff(self):
        subject = '[tst] Reporte de datasets no presentes de Monitoreo Apertura del 2018-10-10'
        self.assertEqual(subject, self.staff_mail.subject)

    def test_send_report(self):
        mail.outbox = []
        send_not_present_reports()
        self.assertEqual(3, len(mail.outbox))

    def test_generator_create_missing_dataset_present_records(self):
        with self.assertRaises(ObjectDoesNotExist):
            _ = self.dataset5.datasetpresentrecord
        self.not_present_report_generator.create_missing_dataset_present_record()
        self.assertEqual(
            Dataset.objects.get(id=self.dataset5.id).datasetpresentrecord.present_record,
            self.dataset5.present)

    def test_sended_only_to_nodes_with_datasets_that_were_present_and_now_they_are_not(self):
        mail.outbox = []
        send_not_present_reports()
        self.assertEqual(3, len(mail.outbox))
        self.assertEqual(['admin4@test.com'], mail.outbox[0].to)
        self.assertEqual(['admin6@test.com'], mail.outbox[1].to)
        self.assertEqual(['staff@test.com'], mail.outbox[2].to)

    def test_task_is_closed(self):
        self.not_present_report_generator.close_task()
        self.assertEqual(NotPresentReportGenerationTask.FINISHED,
                         self.not_present_report_generator.report_task.status)

    def test_addresser_email_is_added_to_bcc(self):
        self.assertEqual(['from_test@test.com'], self.node1_mail.bcc)
        self.assertEqual(['from_test@test.com'], self.node2_mail.bcc)
        self.assertEqual(['from_test@test.com'], self.staff_mail.bcc)

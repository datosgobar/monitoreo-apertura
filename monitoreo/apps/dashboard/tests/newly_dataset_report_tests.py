from __future__ import unicode_literals

import os
import re

from django.contrib.auth.models import User
from django_datajsonar.models import Node, Catalog, Dataset

from monitoreo.apps.dashboard.models.tasks import NewlyReportGenerationTask
from monitoreo.apps.dashboard.report_generators import NewlyDatasetReportGenerator
from monitoreo.apps.dashboard.report_tasks import send_newly_reports
from monitoreo.apps.dashboard.context_managers import suppress_autotime

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


class NewlyDatasetReportGenerationTest(TestCase):

    LAST_REPORT_DATE = timezone.datetime(2010, 10, 10, 10, tzinfo=timezone.utc)
    NOW_FOR_TESTING = timezone.datetime(2018, 10, 10, 10, tzinfo=timezone.utc)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

        config = DynamicEmailConfiguration.get_solo()
        config.from_email = 'from_test@test.com'
        config.save()

        # set mock task
        cls.newly_report_task = NewlyReportGenerationTask.objects.create(finished=cls.LAST_REPORT_DATE,
                                                                         logs='test task logs')
        cls.newly_report_task.status = NewlyReportGenerationTask.FINISHED
        cls.newly_report_task.save()

        # set mock nodes
        cls.node1 = Node.objects.create(catalog_id='id1', catalog_url='url', indexable=True)
        cls.node2 = Node.objects.create(catalog_id='id2', catalog_url='url', indexable=True)
        cls.node3 = Node.objects.create(catalog_id='id3', catalog_url='url', indexable=True)

        cls.node1.admins.create(username='admin1', password='regular', email='admin1@test.com',
                                is_staff=False)
        cls.node2.admins.create(username='admin2', password='regular', email='admin2@test.com',
                                is_staff=False)
        cls.node3.admins.create(username='admin3', password='regular', email='admin3@test.com',
                                is_staff=False)

        # set mock user
        User.objects.create(username='staff', password='staff', email='staff@test.com',
                            is_staff=True)

        cls.catalog1 = Catalog.objects.create(title='id1', identifier='id1')
        cls.catalog2 = Catalog.objects.create(title='id2', identifier='id2')
        cls.catalog3 = Catalog.objects.create(title='id3', identifier='id3')

        cls.dataset1 = Dataset.objects.create(identifier='dataset1', metadata='{}',
                                              catalog=cls.catalog1, indexable=True, present=True, updated=True)
        cls.dataset2 = Dataset.objects.create(identifier='dataset2', metadata='{}',
                                              catalog=cls.catalog2, indexable=True, present=True, updated=True)
        old_date = timezone.datetime(2000, 10, 10, 10, tzinfo=timezone.utc)
        with suppress_autotime(Dataset, 'date_created'):
            cls.dataset3 = Dataset.objects.create(identifier='dataset3', metadata='{}',
                                                  catalog=cls.catalog3, date_created=old_date,
                                                  indexable=True, present=True, updated=True)

        cls.report_task = NewlyReportGenerationTask.objects.create()

        cls.newly_report_generator = NewlyDatasetReportGenerator(cls.report_task, cls.LAST_REPORT_DATE)

    def setUp(self):
        with patch('django.utils.timezone.now', return_value=self.NOW_FOR_TESTING):
            self.newly_report_generator.send_email(
                self.newly_report_generator.generate_email(self.node1),
                node=self.node1)
            self.newly_report_generator.send_email(
                self.newly_report_generator.generate_email(self.node2),
                node=self.node2)
            self.newly_report_generator.send_email(
                self.newly_report_generator.generate_email())
            self.node1_mail = mail.outbox[0]
            self.node2_mail = mail.outbox[1]
            self.staff_mail = mail.outbox[2]

    def tearDown(self):
        mail.outbox = []

    def test_mail_is_sent_to_node_admins(self):
        self.assertEqual(3, len(mail.outbox))
        self.assertEqual(['admin1@test.com'], self.node1_mail.to)
        self.assertEqual(['admin2@test.com'], self.node2_mail.to)

    def test_mail_sent_to_node_is_not_sent_to_other_nodes(self):
        self.assertNotIn('admin2@test.com', self.node1_mail.to)
        self.assertNotIn('admin1@test.com', self.node2_mail.to)

    def test_mail_is_sent_to_staff_members(self):
        self.assertEqual(['staff@test.com'], self.staff_mail.to)

    def test_subject_for_nodes(self):
        subject = 'Reporte de novedades para id1 del 2018-10-10 07:00:00'
        self.assertEqual(subject, self.node1_mail.subject)

    def test_subject_for_staff(self):
        subject = 'Reporte de novedades del 2018-10-10 07:00:00'
        self.assertEqual(subject, self.staff_mail.subject)

    def test_send_report(self):
        mail.outbox = []
        send_newly_reports()
        self.assertEqual(3, len(mail.outbox))

    def test_mail_not_sent_to_nodes_without_new_nodes(self):
        recipients = [mail.to for mail in mail.outbox]
        self.assertNotIn(['admin3@test.com'], recipients)

    def test_task_is_closed(self):
        self.newly_report_generator.close_task()
        self.assertEqual(NewlyReportGenerationTask.FINISHED,
                         self.newly_report_generator.report_task.status)

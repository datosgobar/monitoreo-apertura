from unittest import TestCase

from django_datajsonar.utils.utils import import_string


class TasksAreImportableTest(TestCase):

    def test_report_generation_task_is_importable(self):
        self.assertIsNotNone(import_string('monitoreo.apps.dashboard.models.ReportGenerationTask'))

    def test_validation_report_task_is_importable(self):
        self.assertIsNotNone(import_string('monitoreo.apps.dashboard.models.ValidationReportTask'))

    def test_indicators_generation_task_is_importable(self):
        self.assertIsNotNone(import_string('monitoreo.apps.dashboard.models.IndicatorsGenerationTask'))

    def test_federation_task_is_importable(self):
        self.assertIsNotNone(import_string('monitoreo.apps.dashboard.models.FederationTask'))

    def test_newly_report_generation_task_is_importable(self):
        self.assertIsNotNone(import_string('monitoreo.apps.dashboard.models.NewlyReportGenerationTask'))

    def test_not_present_report_generation_task_is_importable(self):
        self.assertIsNotNone(import_string('monitoreo.apps.dashboard.models.NotPresentReportGenerationTask'))

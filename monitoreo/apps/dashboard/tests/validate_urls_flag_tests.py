from django.test import TestCase
from django_datajsonar.models import Node

from monitoreo.apps.dashboard.models.tasks import TasksConfig


class ValidateURLsFlagTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tasks_config = TasksConfig.get_solo()
        cls.node = Node.objects.create(catalog_url='http://test.catalog.com',
                                       indexable=True,
                                       catalog_id='test_catalog')

    def test_validate_false_if_global_flag_is_false(self):
        self.tasks_config.validation_url_check = False
        flag = self.tasks_config.get_validation_config_for_node(self.node)
        self.assertFalse(flag)

    def test_validate_false_if_global_flag_true_and_node_flag_false(self):
        flag = self.tasks_config.get_validation_config_for_node(self.node)
        self.node.validate_catalog_urls = False
        self.assertFalse(flag)

    def test_validate_true_if_global_flag_true_and_node_flag_true(self):
        self.tasks_config.validation_url_check = True
        self.node.validate_catalog_urls = True

        flag = self.tasks_config.get_validation_config_for_node(self.node)
        self.assertTrue(flag)

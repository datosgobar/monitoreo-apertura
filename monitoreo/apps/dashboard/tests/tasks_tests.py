#! coding: utf-8
import os
try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.conf import settings
from django.test import TestCase
from pydatajson.core import DataJson
from django_datajsonar.apps.management.models import Node
from django_datajsonar.apps.api.models import Catalog, Dataset
from ..tasks import harvest_run, get_dataset_list

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class HarvestRunTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        setattr(settings, 'HARVESTING_URL', 'harvest_url')
        setattr(settings, 'HARVESTING_URL_APIKEY', 'apikey')
        # Set 2 nodes
        node1 = Node(catalog_id='id1', catalog_url=cls.get_sample('full_data.json'), indexable=True)
        node2 = Node(catalog_id='id2', catalog_url=cls.get_sample('minimum_data.json'), indexable=False)
        node1.save()
        node2.save()
        # Set Catalogs and Datasets
        catalog1 = Catalog(title='catalog_1', identifier='id1', metadata='{}', updated=True)
        catalog2 = Catalog(title='catalog_2', identifier='id2', metadata='{}', updated=True)
        catalog1.save()
        catalog2.save()
        for x in range(0, 3):
            dataset = Dataset(identifier='ds_1_'+str(x), metadata='{}', catalog=catalog1,
                              indexable=True, present=True, updated=True)
            dataset.save()
        for x in range(0, 3):
            dataset = Dataset(identifier='ds_2_'+str(x), metadata='{}', catalog=catalog2,
                              indexable=False, present=True, updated=True)
            dataset.save()

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_indexable_node_gets_harvested(self, mock_harvest):
        harvest_run()
        mock_harvest.assert_called_with(DataJson(self.get_sample('full_data.json')), 'harvest_url',
                                        'apikey', 'id1', ['ds_1_0', 'ds_1_1', 'ds_1_2'])

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_unindexable_node_does_not_get_harvested(self, mock_harvest):
        node1 = Node.objects.get(catalog_id='id1')
        node1.indexable = False
        node1.save()
        node2 = Node.objects.get(catalog_id='id2')
        node2.indexable = True
        node2.save()
        harvest_run()
        mock_harvest.assert_called_with(DataJson(self.get_sample('minimum_data.json')),
                                        'harvest_url', 'apikey', 'id2', [])

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_indexable_datasets_get_harvested(self, mock_harvest):
        node2 = Node.objects.get(catalog_id='id2')
        node2.indexable = True
        node2.save()
        dataset = Dataset.objects.get(identifier='ds_2_1')
        dataset.indexable = True
        dataset.save()
        harvest_run()
        mock_harvest.assert_called_with(DataJson(self.get_sample('minimum_data.json')),
                                        'harvest_url', 'apikey', 'id2', ['ds_2_1'])

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_unindexable_datasets_dont_get_harvested(self, mock_harvest):
        dataset = Dataset.objects.get(identifier='ds_1_1')
        dataset.indexable = False
        dataset.save()
        harvest_run()
        mock_harvest.assert_called_with(DataJson(self.get_sample('full_data.json')),
                                        'harvest_url', 'apikey', 'id1', ['ds_1_0', 'ds_1_2'])

    def test_get_dataset_list_return_correct_ids(self):
        node1 = Node.objects.get(catalog_id='id1')
        dataset_list = get_dataset_list(node1)
        self.assertItemsEqual(['ds_1_0', 'ds_1_1', 'ds_1_2'], dataset_list)
        dataset = Dataset.objects.get(identifier='ds_1_1')
        dataset.identifier = 'new_identifier'
        dataset.save()
        dataset_list = get_dataset_list(node1)
        self.assertItemsEqual(['ds_1_0', 'new_identifier', 'ds_1_2'], dataset_list)
        dataset = Dataset.objects.get(identifier='new_identifier')
        dataset.indexable = False
        dataset.save()
        dataset_list = get_dataset_list(node1)
        self.assertItemsEqual(['ds_1_0', 'ds_1_2'], dataset_list)

    def test_get_dataset_list_returns_empty_list_if_there_are_no_related_datasets(self):
        new_node = Node(catalog_id='id3', catalog_url=self.get_sample('full_data.json'), indexable=True)
        dataset_list = get_dataset_list(new_node)
        self.assertItemsEqual([], dataset_list)

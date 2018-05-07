#! coding: utf-8

import os

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.test import TestCase
from pydatajson.core import DataJson
from django_datajsonar.models import Node, Catalog, Dataset
from ..tasks import federation_run, get_dataset_list
from ..models import HarvestingNode

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class HarvestRunTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # Set harvesting node
        harvesting = HarvestingNode(name='aName', url='harvest_url', apikey='apikey', enabled=True)
        harvesting.save()
        # Set nodes
        node1 = Node(catalog_id='id1', catalog_url=cls.get_sample('full_data.json'),
                     indexable=True)
        node2 = Node(catalog_id='id2', catalog_url=cls.get_sample('minimum_data.json'),
                     indexable=True)
        invalid_node = Node(catalog_id='id3', catalog_url=cls.get_sample('missing_dataset_title.json'),
                            indexable=True)
        node1.save()
        node2.save()
        invalid_node.save()
        # Set Catalogs and Datasets
        catalog1 = Catalog(title='catalog_1', identifier='id1', metadata='{}', updated=True)
        catalog2 = Catalog(title='catalog_2', identifier='id2', metadata='{}', updated=True)
        catalog3 = Catalog(title='catalog_3', identifier='id3', metadata='{}', updated=True)
        catalog1.save()
        catalog2.save()
        catalog3.save()
        for cat in [catalog1, catalog2, catalog3]:
            dataset = Dataset(identifier='99db6631-d1c9-470b-a73e-c62daa32c777', metadata='{}',
                              catalog=cat, indexable=True, present=True, updated=True)
            dataset.save()

        dataset2 = Dataset(identifier='99db6631-d1c9-470b-a73e-c62daa32c420', metadata='{}',
                           catalog=catalog1, indexable=True, present=True, updated=True)
        dataset2.save()

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_indexable_node_gets_harvested(self, mock_harvest):
        federation_run()
        self.assertEqual(3, len(mock_harvest.mock_calls))

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_unindexable_node_does_not_get_harvested(self, mock_harvest):
        node1 = Node.objects.get(catalog_id='id1')
        node1.indexable = False
        node1.save()
        federation_run()
        self.assertEqual(2, len(mock_harvest.mock_calls))

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_indexable_datasets_get_harvested(self, mock_harvest):
        federation_run()
        mock_harvest.assert_any_call(DataJson(self.get_sample('minimum_data.json')),
                                     'harvest_url', 'apikey', 'id2',
                                     ['99db6631-d1c9-470b-a73e-c62daa32c777'])

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_unindexable_datasets_dont_get_harvested(self, mock_harvest):
        Dataset.objects.all().update(indexable=False)
        federation_run()
        mock_harvest.assert_any_call(DataJson(self.get_sample('full_data.json')),
                                     'harvest_url', 'apikey', 'id1', [])
        mock_harvest.assert_any_call(DataJson(self.get_sample('minimum_data.json')),
                                     'harvest_url', 'apikey', 'id2', [])
        mock_harvest.assert_any_call(DataJson(self.get_sample('missing_dataset_title.json')),
                                     'harvest_url', 'apikey', 'id3', [])

    @patch('monitoreo.apps.dashboard.tasks.harvest_catalog_to_ckan', autospec=True)
    def test_invalid_datasets_dont_get_harvested(self, mock_harvest):
        federation_run()
        mock_harvest.assert_any_call(DataJson(self.get_sample('missing_dataset_title.json')),
                                     'harvest_url', 'apikey', 'id3', [])

    def test_get_dataset_list_return_correct_ids(self):
        node1 = Node.objects.get(catalog_id='id1')
        datajson = DataJson(self.get_sample('full_data.json'))
        dataset_list = get_dataset_list(node1, datajson)
        self.assertItemsEqual(['99db6631-d1c9-470b-a73e-c62daa32c777',
                               '99db6631-d1c9-470b-a73e-c62daa32c420'],
                              dataset_list)
        dataset = Dataset.objects.get(catalog__identifier='id1',
                                      identifier='99db6631-d1c9-470b-a73e-c62daa32c777')
        dataset.identifier = 'new_identifier'
        dataset.save()
        dataset = datajson.get_dataset(identifier='99db6631-d1c9-470b-a73e-c62daa32c777')
        dataset['identifier'] = 'new_identifier'
        dataset_list = get_dataset_list(node1, datajson)
        self.assertItemsEqual(['new_identifier',
                               '99db6631-d1c9-470b-a73e-c62daa32c420'],
                              dataset_list)
        dataset = Dataset.objects.get(catalog__identifier='id1',
                                      identifier='new_identifier')
        dataset.indexable = False
        dataset.save()
        dataset_list = get_dataset_list(node1, datajson)
        self.assertItemsEqual(['99db6631-d1c9-470b-a73e-c62daa32c420'],
                              dataset_list)

    def test_dataset_list_returns_empty_if_no_related_datasets(self):
        new_node = Node(catalog_id='id4', catalog_url=self.get_sample('full_data.json'), indexable=True)
        dataset_list = get_dataset_list(new_node, DataJson(self.get_sample('full_data.json')))
        self.assertItemsEqual([], dataset_list)

    def test_get_dataset_does_not_return_invalid_datasets(self):
        node = Node.objects.get(catalog_id='id3')
        datajson = DataJson(self.get_sample('missing_dataset_title.json'))
        dataset_list = get_dataset_list(node, datajson)
        self.assertItemsEqual([], dataset_list)
        dataset = datajson.get_dataset(identifier='99db6631-d1c9-470b-a73e-c62daa32c777')
        dataset['title'] = 'aTitle'
        dataset_list = get_dataset_list(node, datajson)
        self.assertItemsEqual(['99db6631-d1c9-470b-a73e-c62daa32c777'], dataset_list)

    def test_get_dataset_does_not_return_missing_datasets(self):
        node = Node.objects.get(catalog_id='id1')
        datajson = DataJson(self.get_sample('full_data.json'))
        datajson.datasets.pop(0)
        dataset_list = get_dataset_list(node, datajson)
        self.assertItemsEqual(['99db6631-d1c9-470b-a73e-c62daa32c420'], dataset_list)


#! coding: utf-8
import os
import json

from mock import patch

from django.test import TestCase
from django_datajsonar.models import Node

from monitoreo.apps.dashboard.models import IndicatorsGenerationTask
from monitoreo.apps.dashboard.helpers import load_catalogs
from pydatajson import DataJson

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class LoadCatalogsTest(TestCase):

    catalog_id = 'test_catalog'

    @classmethod
    def setUpTestData(cls):
        cls.node = Node(catalog_id=cls.catalog_id,
                        catalog_url=os.path.join(dir_path, 'full_data.json'),
                        catalog_format='json',
                        indexable=True)
        cls.node.catalog = json.dumps(DataJson(cls.node.catalog_url))
        cls.node.save()
        cls.task = IndicatorsGenerationTask.objects.create()
        cls.catalogs = load_catalogs(cls.task, Node.objects.all())

    def test_method_returns_non_empty_list(self):
        self.assertTrue(self.catalogs, 'Lista no vacía')

    def test_returned_dicts_are_datajson_parseable(self):
        one_catalog = self.catalogs[-1]
        indicators, _ = DataJson().generate_catalogs_indicators(one_catalog)
        # Asumo que si tiene el indicador de datasets fue parseado exitosamente
        self.assertTrue(indicators[0]['datasets_cant'], 'Catálogo no parseado')

    def test_load_catalog_json_node_format(self):
        def mock_side_effect(catalog, catalog_format=None,
                             verify_ssl=False):
            return {'format': catalog_format}

        with patch('monitoreo.apps.dashboard.helpers.DataJson',
                   side_effect=mock_side_effect):
            result = load_catalogs(self.task, Node.objects.all())
        self.assertEqual([{'identifier': 'test_catalog', 'format': 'json'}],
                         result)

    def test_load_catalog_xlsx_node_format(self):
        def mock_side_effect(catalog, catalog_format=None,
                             verify_ssl=False):
            return {'format': catalog_format}

        self.node.catalog_format = 'xlsx'
        self.node.save()
        with patch('monitoreo.apps.dashboard.helpers.DataJson',
                   side_effect=mock_side_effect):
            result = load_catalogs(self.task, Node.objects.all())
        self.assertEqual([{'identifier': 'test_catalog', 'format': 'xlsx'}],
                         result)

#! coding: utf-8
import os
import json
from datetime import date, timedelta
from django.test import TestCase
from django_datajsonar.models import Node, ReadDataJsonTask
from monitoreo.apps.dashboard.models import Indicador, IndicatorType
from monitoreo.apps.dashboard.helpers import fetch_latest_indicadors, \
    load_catalogs
from pydatajson import DataJson

dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class FetchLatestIndicatorsTest(TestCase):

    def setUp(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        test_type = IndicatorType.objects.create(nombre='test_type')
        test_type.save()

        old = Indicador.objects.create(indicador_tipo=test_type,
                                       jurisdiccion_nombre='test catalog',
                                       indicador_valor='old value')
        # Override a la fecha guardada por default
        old.fecha = yesterday
        old.save()

        Indicador.objects.create(indicador_tipo=test_type,
                                 jurisdiccion_nombre='Test catalog',
                                 indicador_valor='latest value').save()
        Indicador.objects.create(indicador_tipo=test_type,
                                 jurisdiccion_nombre='Test catalog',
                                 indicador_valor='latest value').save()

        other_type = IndicatorType.objects.create(nombre='other_type')
        other_type.save()

        Indicador.objects.create(indicador_tipo=other_type,
                                 jurisdiccion_nombre='Test catalog',
                                 indicador_valor='valor independiente a '
                                                 'test_type').save()

    def test_latest_fetched(self):
        indicators = Indicador.objects.all()
        expected = {
            'test_type': 'latest value'
        }
        latest = fetch_latest_indicadors(indicators)
        self.assertDictContainsSubset(expected, latest, 'Indicador fetcheado '
                                                        'no es el más reciente')


class LoadCatalogsTest(TestCase):

    catalog_id = 'test_catalog'

    @classmethod
    def setUpTestData(cls):
        cls.node = Node(catalog_id=cls.catalog_id,
                        catalog_url=os.path.join(dir_path, 'full_data.json'),
                        indexable=True)
        cls.node.catalog = json.dumps(DataJson(cls.node.catalog_url))
        cls.node.save()
        task = ReadDataJsonTask.objects.create()
        cls.catalogs = load_catalogs(task, Node.objects.all())

    def test_method_returns_non_empty_list(self):
        self.assertTrue(self.catalogs, 'Lista no vacía')

    def test_returned_dicts_are_datajson_parseable(self):
        one_catalog = self.catalogs[-1]
        indicators, _ = DataJson().generate_catalogs_indicators(one_catalog)
        # Asumo que si tiene el indicador de datasets fue parseado exitosamente
        self.assertTrue(indicators[0]['datasets_cant'], 'Catálogo no parseado')

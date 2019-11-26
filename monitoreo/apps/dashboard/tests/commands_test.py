#! coding: utf-8
import json
import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django_datajsonar.models import Node
from mock import patch
from pydatajson import DataJson

from monitoreo.apps.dashboard.helpers import load_catalogs
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, TableColumn, IndicatorsGenerationTask, \
    HarvestingNode
from monitoreo.apps.dashboard.models.tasks import TasksConfig

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class CommandTest(TestCase):
    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        HarvestingNode.objects.create(
            name='aName', url='harvest_url', apikey='apikey', enabled=True)
        Node.objects.create(catalog_id='id1',
                            catalog_url=cls.get_sample('full_data.json'),
                            indexable=True)
        Node.objects.create(catalog_id='id2',
                            catalog_url=cls.get_sample('minimum_data.json'),
                            indexable=True)
        HarvestingNode.objects.create(
            catalog_id='idx1',
            name='indexador1',
            url=cls.get_sample('catalogo_justicia.json'),
            apikey='apikey',
            enabled=True)
        HarvestingNode.objects.create(
            catalog_id='idx2',
            name='indexador2',
            url=cls.get_sample('full_data.json'),
            apikey='apikey',
            enabled=True)
        task = IndicatorsGenerationTask.objects.create()
        cls.catalogs = load_catalogs(task, Node.objects.all())
        # Quiero que los cargue por el path, no como url. Uso harvesting=False
        cls.indexing_catalogs = load_catalogs(task,
                                              HarvestingNode.objects.all())
        central = DataJson(cls.get_sample('full_data.json'))
        cls.indicators, cls.network_indicators = \
            DataJson().generate_catalogs_indicators(cls.catalogs,
                                                    central_catalog=central,
                                                    identifier_search=True,
                                                    broken_links=True)
        cls.indexing_indicators, _ = \
            DataJson().generate_catalogs_indicators(cls.indexing_catalogs,
                                                    identifier_search=True,
                                                    broken_links=True)
        config = TasksConfig.get_solo()
        config.indicators_url_check = True
        config.save()

        cls.dj = DataJson()
        with patch('monitoreo.apps.dashboard.indicators_tasks.CENTRAL',
                   cls.get_sample('full_data.json')):
            call_command('indicadores')

    def test_indicators_created(self):
        self.assertTrue(Indicador.objects.all())

    def test_network_indicators_created(self):
        self.assertTrue(IndicadorRed.objects.all())

    def test_verify_network_indicators(self):
        indicators = IndicadorRed.objects.all()
        for network_indicator, value in self.network_indicators.items():
            indicator = indicators.filter(indicador_tipo__nombre=network_indicator)
            self.assertTrue(indicator, 'Query vacia: filtro por ' + network_indicator)
            indicator = indicator[0]
            value = json.loads(json.dumps(value))
            self.assertEqual(json.loads(indicator.indicador_valor), value)

    def test_verify_individual_indicators(self):
        for catalog in self.catalogs:
            # Obtengo los indicadores calculados directamente con DataJson
            catalog_index = self.catalogs.index(catalog)
            calculated_indicators = self.indicators[catalog_index]

            indics = Indicador.objects.filter(
                jurisdiccion_id=catalog['identifier'])
            for indicator in indics:
                name = indicator.indicador_tipo.nombre
                value = json.loads(json.dumps(calculated_indicators[name]))
                self.assertEqual(json.loads(indicator.indicador_valor), value)

    def test_verify_indexing_indicators(self):
        for catalog in self.indexing_catalogs:
            # Obtengo los indicadores calculados directamente con DataJson
            catalog_index = self.indexing_catalogs.index(catalog)
            calculated_indicators = self.indexing_indicators[catalog_index]

            indics = Indicador.objects.filter(
                jurisdiccion_id=catalog['identifier'])
            for indicator in indics:
                name = indicator.indicador_tipo.nombre
                value = json.loads(json.dumps(calculated_indicators[name]))
                self.assertEqual(json.loads(indicator.indicador_valor), value)

    def test_columns_are_created(self):
        for column in settings.DEFAULT_INDICATORS:
            self.assertTrue(TableColumn.objects.get(indicator__nombre=column))

    def test_task_is_created(self):
        # Una creada en el setup y otra por el command
        self.assertEqual(2, IndicatorsGenerationTask.objects.count())

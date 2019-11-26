#! coding: utf-8

import os

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from pydatajson import DataJson

from monitoreo.apps.dashboard.models import IndicatorsGenerationTask, Indicador
from monitoreo.apps.dashboard.models import IndicadorRed, TableColumn
from monitoreo.apps.dashboard.models import IndicatorType, IndicadorFederador
from monitoreo.apps.dashboard.models import HarvestingNode, CentralNode
from monitoreo.apps.dashboard.indicators_tasks import generate_indicators, CENTRAL


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


@patch('monitoreo.apps.dashboard.indicators_tasks.load_catalogs', autospec=True)
@patch('monitoreo.apps.dashboard.indicators_tasks.DataJson.generate_catalogs_indicators', autospec=True)
class IndicatorGenerationsTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    def setUp(self):
        # set mock default indicators
        settings.DEFAULT_INDICATORS = ['ind_a', 'ind_b', 'ind_c', ]
        settings.INDICATORS_INFO = [{"indicador_nombre": "ind_a", "indicador_nombre_tabla": "col_a"},
                                    {"indicador_nombre": "ind_b", "indicador_nombre_tabla": "col_b"},
                                    {"indicador_nombre": "ind_c", "indicador_nombre_tabla": "col_c"}]
        # set mock catalog list
        self.catalogs = [DataJson(self.get_sample(cat)) for cat in ['full_data.json', 'catalogo_justicia.json']]
        # set mock indicators
        self.indicator_1 = {'identifier': 'a', 'title': self.catalogs[0]['title'], 'ind_a': 0, 'ind_b': 1, 'ind_c': 2}
        self.indicator_2 = {'identifier': 'b', 'title': self.catalogs[1]['title'], 'ind_a': 3, 'ind_b': None, 'ind_c': 2}
        self.indicators = [self.indicator_1, self.indicator_2]
        self.network_indicators = {'ind_a': 3, 'ind_b': 1, 'ind_c': 4}

    def test_task_is_finished(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        task.refresh_from_db()
        self.assertEqual(IndicatorsGenerationTask.FINISHED, task.status)

    def test_indicator_models_are_created(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        self.assertEqual(6, Indicador.objects.count())
        self.assertEqual(3, IndicadorRed.objects.count())
        self.assertEqual(3, Indicador.objects.filter(jurisdiccion_nombre=self.catalogs[0]['title']).count())
        self.assertEqual(3, Indicador.objects.filter(jurisdiccion_nombre=self.catalogs[1]['title']).count())
        self.assertEqual(3, IndicadorFederador.objects.filter(jurisdiccion_nombre=self.catalogs[0]['title']).count())
        self.assertEqual(3, IndicadorFederador.objects.filter(jurisdiccion_nombre=self.catalogs[1]['title']).count())

    def test_default_columns_are_created(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        self.assertEqual(3, TableColumn.objects.count())
        self.assertEqual(1, TableColumn.objects.filter(full_name='col_a').count())
        self.assertEqual(1, TableColumn.objects.filter(full_name='col_b').count())
        self.assertEqual(1, TableColumn.objects.filter(full_name='col_c').count())

    def test_indicators_are_updated_without_replication(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        self.indicator_2['ind_b'] = 10

        self.indicator_1['identifier'] = 'a'
        self.indicator_2['identifier'] = 'b'

        self.indicator_1['title'] = self.catalogs[0]['title']
        self.indicator_2['title'] = self.catalogs[1]['title']

        generate_indicators(task)
        self.assertEqual(6, Indicador.objects.count())
        self.assertEqual(3, IndicadorRed.objects.count())
        ind_type = IndicatorType.objects.get(nombre='ind_b', tipo='RED')
        self.assertEqual('10', Indicador.objects.get(jurisdiccion_nombre=self.catalogs[1]['title'],
                                                     indicador_tipo=ind_type).indicador_valor)

    def test_indicators_store_correct_date(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        with patch('monitoreo.apps.dashboard.indicators_tasks.timezone') as mock_time:
            time = timezone.localtime().replace(hour=5, minute=0)
            mock_time.localtime.return_value = time
            task1 = IndicatorsGenerationTask.objects.create()
            generate_indicators(task1)

        self.indicator_2['ind_b'] = 10

        self.indicator_1['identifier'] = 'a'
        self.indicator_2['identifier'] = 'b'

        self.indicator_1['title'] = self.catalogs[0]['title']
        self.indicator_2['title'] = self.catalogs[1]['title']

        with patch('monitoreo.apps.dashboard.indicators_tasks.timezone') as mock_time:
            time = timezone.localtime().replace(hour=23, minute=0)
            mock_time.localtime.return_value = time
            task2 = IndicatorsGenerationTask.objects.create()
            generate_indicators(task2)

        self.assertEqual(6, Indicador.objects.count())
        self.assertEqual(3, IndicadorRed.objects.count())
        ind_type = IndicatorType.objects.get(nombre='ind_b', tipo='RED')
        self.assertEqual('10', Indicador.objects.get(jurisdiccion_nombre=self.catalogs[1]['title'],
                                                     indicador_tipo=ind_type).indicador_valor)

    def test_central_node_default(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        mock_indic.assert_any_call(DataJson(), self.catalogs,
                                   identifier_search=True,
                                   broken_links=False)
        mock_indic.assert_any_call(DataJson(), self.catalogs, CENTRAL,
                                   identifier_search=True,
                                   broken_links=False)

    def test_undefined_central_node_uses_default(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        CentralNode.objects.create()
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        mock_indic.assert_any_call(DataJson(), self.catalogs,
                                   identifier_search=True,
                                   broken_links=False)
        mock_indic.assert_any_call(DataJson(), self.catalogs, CENTRAL,
                                   identifier_search=True,
                                   broken_links=False)

    def test_defined_central_node_catalog(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        harvesting = HarvestingNode.objects.create(
            name='aName', url='harvest_url/', apikey='apikey', enabled=True)
        CentralNode.objects.create(node=harvesting)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task)
        mock_indic.assert_any_call(DataJson(), self.catalogs,
                                   identifier_search=True,
                                   broken_links=False)
        mock_indic.assert_any_call(DataJson(), self.catalogs,
                                   'harvest_url/data.json',
                                   identifier_search=True,
                                   broken_links=False)

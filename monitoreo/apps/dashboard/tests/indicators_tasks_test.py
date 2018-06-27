#! coding: utf-8

import os

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings

from pydatajson import DataJson

from monitoreo.apps.dashboard.models import IndicatorsGenerationTask, Indicador, IndicadorRed, TableColumn
from monitoreo.apps.dashboard.indicators_tasks import generate_indicators


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


@patch('monitoreo.apps.dashboard.indicators_tasks.load_catalogs', autospec=True)
@patch('monitoreo.apps.dashboard.indicators_tasks.DataJson.generate_catalogs_indicators', autospec=True)
class IndicatorGenerationsTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock default indicators
        settings.DEFAULT_INDICATORS = ['ind_a', 'ind_b', 'ind_c', ]
        settings.INDICATORS_INFO = [{"indicador_nombre": "ind_a", "indicador_nombre_tabla": "col_a"},
                                    {"indicador_nombre": "ind_b", "indicador_nombre_tabla": "col_b"},
                                    {"indicador_nombre": "ind_c", "indicador_nombre_tabla": "col_c"}]
        # set mock catalog list
        cls.catalogs = [DataJson(cls.get_sample(cat)) for cat in ['full_data.json', 'catalogo_justicia.json']]
        # set mock indicators
        cls.indicator_1 = {'ind_a': 0, 'ind_b': 1, 'ind_c': 2}
        cls.indicator_2 = {'ind_a': 3, 'ind_b': None, 'ind_c': 2}
        cls.indicators = [cls.indicator_1, cls.indicator_2]
        cls.network_indicators = {'ind_a': 3, 'ind_b': 1, 'ind_c': 4}

    def test_task_is_finished(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task.pk)
        task.refresh_from_db()
        self.assertEqual(IndicatorsGenerationTask.FINISHED, task.status)

    def test_indicator_models_are_created(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task.pk)
        self.assertEqual(6, Indicador.objects.count())
        self.assertEqual(3, IndicadorRed.objects.count())
        self.assertEqual(3, Indicador.objects.filter(jurisdiccion_nombre=self.catalogs[0]['title']).count())
        self.assertEqual(3, Indicador.objects.filter(jurisdiccion_nombre=self.catalogs[1]['title']).count())

    def test_default_columns_are_created(self, mock_indic, mock_load):
        mock_load.return_value = self.catalogs
        mock_indic.return_value = (self.indicators, self.network_indicators)
        task = IndicatorsGenerationTask.objects.create()
        generate_indicators(task.pk)
        self.assertEqual(3, TableColumn.objects.count())
        self.assertEqual(1, TableColumn.objects.filter(full_name='col_a').count())
        self.assertEqual(1, TableColumn.objects.filter(full_name='col_b').count())
        self.assertEqual(1, TableColumn.objects.filter(full_name='col_c').count())

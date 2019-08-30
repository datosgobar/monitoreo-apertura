#! coding: utf-8

import os
import tempfile
import csv

from datetime import date

from django.test import TestCase
from django.core.management import call_command

from monitoreo.apps.dashboard.models import Indicador
from monitoreo.apps.dashboard.models import IndicadorRed
from monitoreo.apps.dashboard.models import IndicatorType
from monitoreo.apps.dashboard.management.indicators_validator import \
    ValidationError
from monitoreo.apps.dashboard.context_managers import suppress_autotime


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')
RESULTS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results')


class IndicatorImportExportTest(TestCase):
    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def get_result(cls, result_filename):
        return os.path.join(RESULTS_DIR, result_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED', id=1)
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED', id=2)
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED',
                                              resumen=True, id=3)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED',
                                              resumen=True, mostrar=False,
                                              id=4)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED',
                                              mostrar=False, id=5)

        types = [type_a, type_b, type_c, type_d, type_e]
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}',
                  '100', '1']
        creation_date = date(2000, 1, 1)
        with suppress_autotime(IndicadorRed, ['fecha']):
            for t, v in zip(types, values):
                IndicadorRed.objects.create(indicador_tipo=t,
                                            indicador_valor=v,
                                            fecha=creation_date)

        with suppress_autotime(Indicador, ['fecha']):
            values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
            for t, v in zip(types, values):
                Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                         jurisdiccion_id='id1',
                                         jurisdiccion_nombre='nodo1',
                                         fecha=creation_date)
            values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
            for t, v in zip(types, values):
                Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                         jurisdiccion_id='id2',
                                         jurisdiccion_nombre='nodo2',
                                         fecha=creation_date)

    def compare_csv(self, expected_file, result_file):
        expected_csv = set(map(tuple, csv.reader(expected_file)))
        result_csv = set(map(tuple, csv.reader(result_file)))
        self.assertSetEqual(expected_csv, result_csv)

    def test_indicators_are_imported_correctly(self):
        indicators_csv = self.get_sample('indicators_sample.csv')
        call_command('import_indicators', indicators_csv)
        future_date = date(2100, 12, 31)
        past_date = date(2000, 1, 1)
        self.assertEqual(0, Indicador.objects.all().
                         filter(fecha=past_date).count())
        self.assertEqual(10, Indicador.objects.all().
                         filter(fecha=future_date).count())
        self.assertEqual('337',
                         Indicador.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_a',
                             jurisdiccion_id='id1').indicador_valor)
        self.assertEqual('[["d3", "l3"]]',
                         Indicador.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_b',
                             jurisdiccion_id='id1').indicador_valor)
        self.assertEqual('{"k1": 100, "k2": 10}',
                         Indicador.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_c',
                             jurisdiccion_id='id2').indicador_valor)

    def test_indicators_are_overwritten(self):
        indicators_csv = self.get_sample('updated_indicators.csv')
        call_command('import_indicators', indicators_csv)
        past_date = date(2000, 1, 1)
        self.assertEqual(10, Indicador.objects.all().count())
        self.assertEqual('337',
                         Indicador.objects.get(
                             fecha=past_date,
                             indicador_tipo__nombre='ind_a',
                             jurisdiccion_id='id1').indicador_valor)
        self.assertEqual('[["d3", "l3"]]',
                         Indicador.objects.get(
                             fecha=past_date,
                             indicador_tipo__nombre='ind_b',
                             jurisdiccion_id='id1').indicador_valor)
        self.assertEqual('{"k1": 100, "k2": 10}',
                         Indicador.objects.get(
                             fecha=past_date,
                             indicador_tipo__nombre='ind_c',
                             jurisdiccion_id='id2').indicador_valor)

    def test_network_indicators_are_imported_correctly(self):
        indicators_csv = self.get_sample('network_indicators_sample.csv')
        future_date = date(2100, 12, 31)
        past_date = date(2000, 1, 1)
        call_command('import_indicators', indicators_csv, type='network')
        self.assertEqual(0, IndicadorRed.objects.all().
                         filter(fecha=past_date).count())
        self.assertEqual(5, IndicadorRed.objects.all().
                         filter(fecha=future_date).count())
        self.assertEqual('1337',
                         IndicadorRed.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_a').indicador_valor)
        self.assertEqual('[["d3", "l3"], ["d4", "l4"]]',
                         IndicadorRed.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_b').indicador_valor)
        self.assertEqual('{"k1": 100, "k2": 20}',
                         IndicadorRed.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_c').indicador_valor)
        self.assertEqual('6500',
                         IndicadorRed.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_d').indicador_valor)
        self.assertEqual('-1',
                         IndicadorRed.objects.get(
                             fecha=future_date,
                             indicador_tipo__nombre='ind_e').indicador_valor)

    def test_malformed_indicators_raise_errors(self):
        error_samples = [
            'repeated_indicators.csv',
            'null_indicators.csv',
            'malformed_date.csv',
            'missing_header.csv',
        ]
        for sample in error_samples:
            with self.assertRaises(ValidationError):
                indicators_csv = self.get_sample(sample)
                call_command('import_indicators', indicators_csv)

    def test_indicators_are_exported_corectly(self):
        result_filename = self.get_result('expected_indicators.csv')
        with tempfile.NamedTemporaryFile(mode='w+t') as tmp_result:
            call_command('export_indicators', tmp_result.name)
            with open(result_filename, 'r') as expected_csv:
                self.compare_csv(expected_csv, tmp_result)

    def test_network_indicators_are_exported_corectly(self):
        result_filename = self.get_result('expected_indicators_aggregated.csv')
        with tempfile.NamedTemporaryFile(mode='w+t') as tmp_result:
            call_command('export_indicators', tmp_result.name, type='network')
            with open(result_filename, 'r') as expected_csv:
                self.compare_csv(expected_csv, tmp_result)

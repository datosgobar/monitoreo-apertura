#! coding: utf-8

import os
import tempfile

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


class IndicatorImportExportTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

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

    def test_indicators_are_imported_correctly(self):
        indicators_csv = self.get_sample('indicators_sample.csv')
        call_command('import_indicators', indicators_csv)

    def test_indicators_are_updated(self):
        pass

    def test_network_indicators_are_imported_correctly(self):
        indicators_csv = self.get_sample('network_indicators_sample.csv')
        call_command('import_indicators', indicators_csv, aggregated=True)

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
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        tmpfile.close()
        call_command('export_indicators', tmpfile.name)
        os.remove(tmpfile.name)
        # self.assertSetEqual()

    def test_network_indicators_are_exported_corectly(self):
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        tmpfile.close()
        call_command('export_indicators', tmpfile.name, aggregated=True)
        os.remove(tmpfile.name)
        # self.assertSetEqual()

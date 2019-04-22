#! coding: utf-8

import os

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.conf import settings

from monitoreo.apps.dashboard.models import Indicador
from monitoreo.apps.dashboard.models import IndicadorRed
from monitoreo.apps.dashboard.models import IndicatorType


SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class IndicatorImportTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

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
        for t, v in zip(types, values):
            IndicadorRed.objects.create(indicador_tipo=t, indicador_valor=v)
        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                     jurisdiccion_id='id1',
                                     jurisdiccion_nombre='nodo1')
        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                     jurisdiccion_id='id2',
                                     jurisdiccion_nombre='nodo2')

    def indicators_are_imported_correctly(self):
        pass

    def repeated_indicators_are_handled_correctly(self):
        pass

    def indicators_are_exported_corectly(self):
        pass


class IndicatorExportTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock env
        settings.ENV_TYPE = 'tst'

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
        for t, v in zip(types, values):
            IndicadorRed.objects.create(indicador_tipo=t, indicador_valor=v)
        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                     jurisdiccion_id='id1',
                                     jurisdiccion_nombre='nodo1')
        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                     jurisdiccion_id='id2',
                                     jurisdiccion_nombre='nodo2')

    def indicators_are_imported_correctly(self):
        pass

    def repeated_indicators_are_handled_correctly(self):
        pass

    def indicators_are_exported_corectly(self):
        pass


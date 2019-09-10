#! coding: utf-8

import os
import shutil
import tempfile

from django_datajsonar.models import Node

try:
    from mock import patch, MagicMock
except ImportError:
    from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.conf import settings

from monitoreo.apps.dashboard.models import Indicador
from monitoreo.apps.dashboard.models import IndicadorRed
from monitoreo.apps.dashboard.models import IndicatorType, IndicadorFederador
from monitoreo.apps.dashboard.models import HarvestingNode, CentralNode
from monitoreo.apps.dashboard.indicators_tasks import write_time_series_files

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'samples')


class IndicatorGenerationsTest(TestCase):

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(SAMPLES_DIR, sample_filename)

    @classmethod
    def setUpTestData(cls):
        # set mock nodes
        cls.node1 = Node.objects.create(catalog_id='id1', catalog_url='url',
                                        indexable=True)
        cls.node2 = Node.objects.create(catalog_id='id2', catalog_url='url',
                                        indexable=True)

        cls.harvest_node = HarvestingNode.objects.create(catalog_id='harvest_id',
                                                         name='harvest node',
                                                         url='http://datos.test.ar',
                                                         apikey='apikey',
                                                         enabled=True)
        central_node = CentralNode.get_solo()
        central_node.node = cls.harvest_node
        central_node.save()

        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED',
                                              resumen=True)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED',
                                              resumen=True, mostrar=False)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED',
                                              mostrar=False)

        types = [type_a, type_b, type_c, type_d, type_e]
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}', '100',
                  '1']
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

        values = ['23', '[["d2", "l2"]]', '{"k2": 1}', '2', '3']
        for t, v in zip(types, values):
            IndicadorFederador.objects.create(indicador_tipo=t, indicador_valor=v,
                                              jurisdiccion_id='harvest_id',
                                              jurisdiccion_nombre='harvest node')

    def test_network_static_file_is_created(self):
        write_time_series_files()
        filepath = os.path.join(settings.MEDIA_ROOT, 'indicator_files', 'indicadores-red-series.csv')
        self.assertTrue(os.path.exists(filepath))

    def test_nodes_static_file_are_created(self):
        write_time_series_files()
        dir_path = os.path.join(settings.MEDIA_ROOT, 'indicator_files', 'nodes')
        for node in Node.objects.all():
            filepath = os.path.join(dir_path, f'indicadores-{node.catalog_id}-series.csv')
            self.assertTrue(os.path.exists(filepath))

    def test_federators_files_are_created(self):
        write_time_series_files()
        dir_path = os.path.join(settings.MEDIA_ROOT, 'indicator_files', 'federator-nodes')
        for node in HarvestingNode.objects.all():
            filepath = os.path.join(dir_path, f'indicadores-{node.catalog_id}-series.csv')
            self.assertTrue(os.path.exists(filepath))

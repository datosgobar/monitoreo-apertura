#! coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from django.test import TestCase
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from django.core.management import call_command

from django_datajsonar.models import Node

from monitoreo.apps.dashboard.models import IndicatorType, TableColumn, IndicadorRed, Indicador

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


class ModelsTest(TestCase):
    indicator_name = "Indicador test"
    indicator_full_name = "Nombre completo del indicador test"

    indicators_info = [{
        "indicador_nombre": indicator_name,
        "indicador_nombre_tabla": indicator_full_name
    }]

    @classmethod
    def setUpTestData(cls):
        _type = IndicatorType(nombre=cls.indicator_name, tipo="TEST")
        _type.save()

        # Tipos de indicadores
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED')

        types = [type_a, type_b, type_c]

        # Indicadores agregados
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k3":3, "k2": 1, "k1": 2}']
        for ind_type, value in zip(types, values):
            IndicadorRed.objects.create(indicador_tipo=ind_type, indicador_valor=value)

        values = ['23', '[["d1", "l1"]]', '{"k1":1, "k2": 2, "k3": 10}']
        old_ids = []
        for ind_type, value in zip(types, values):
            old = IndicadorRed.objects.create(indicador_tipo=ind_type, indicador_valor=value)
            old_ids.append(old.id)
        # Necesario para agregar los indicadores con fecha distinta a la de hoy
        cls.past_date = parse_datetime('2000-01-01 12:00:00Z')
        IndicadorRed.objects.filter(id__in=old_ids).update(fecha=cls.past_date)

        # Indicadores
        values = ['22', '["d1", "l1"]', '{"k3":2, "k1": 2}']
        for ind_type, value in zip(types, values):
            Indicador.objects.create(indicador_tipo=ind_type, indicador_valor=value,
                                     jurisdiccion_nombre='catalogo_de_test_1',
                                     jurisdiccion_id='test_1')

        values = ['20', '["d2", "l2"]', '{"k3":1, "k2": 1}']
        for ind_type, value in zip(types, values):
            Indicador.objects.create(indicador_tipo=ind_type, indicador_valor=value,
                                     jurisdiccion_nombre='catalogo_de_test_2',
                                     jurisdiccion_id='test_2')

        Indicador.objects.create(indicador_tipo=type_a, indicador_valor='00',
                                 jurisdiccion_nombre='catalogo_de_test_2',
                                 jurisdiccion_id=None)

    def test_indicators_created(self):
        with self.settings(INDICATORS_INFO=self.indicators_info):
            column = TableColumn(
                indicator=IndicatorType.objects.get(nombre=self.indicator_name))
            column.clean()
            column.save()
            self.assertEqual(column.full_name, self.indicator_full_name)

    def test_sorting_indicators(self):
        expected_one_dimensional = {'ind_a': 42}
        expected_listed = {'ind_b': [["d1", "l1"], ["d2", "l2"]]}
        expected_multi_dimensional = {'ind_c': OrderedDict([('k3', 3), ('k1', 2), ('k2', 1)])}

        one_dimensional, multi_dimensional, listed = IndicadorRed\
            .objects.sorted_indicators_on_date(now().date())

        self.assertDictEqual(expected_listed, listed)
        self.assertDictEqual(expected_multi_dimensional, multi_dimensional)
        self.assertDictEqual(expected_one_dimensional, one_dimensional)

        expected_one_dimensional = {'ind_a': 23}
        expected_listed = {'ind_b': [["d1", "l1"], ]}
        expected_multi_dimensional = {'ind_c': OrderedDict([('k3', 10), ('k2', 2), ('k1', 1)])}

        one_dimensional, multi_dimensional, listed = IndicadorRed \
            .objects.sorted_indicators_on_date(self.past_date)

        self.assertDictEqual(expected_listed, listed)
        self.assertDictEqual(expected_multi_dimensional, multi_dimensional)
        self.assertDictEqual(expected_one_dimensional, one_dimensional)

    def test_get_numerical_network_indicators(self):
        expected_network_indics = {now().date(): {'ind_a': 42},
                                   parse_datetime('2000-01-01 12:00:00Z')
                                   .date(): {'ind_a': 23}}
        network_indics = IndicadorRed.objects.numerical_indicators_by_date()
        self.assertDictEqual(expected_network_indics, network_indics)

    def test_get_node_network_indicators(self):
        expected_node_indics = {now().date(): {'ind_a': 22}}
        node_indics = Indicador.objects.numerical_indicators_by_date(
            node_id='test_1')
        self.assertDictEqual(expected_node_indics, node_indics)

    def test_remove_duplicated_indicators(self):
        # Duplicar indicadores
        self.duplicate_indicators(IndicadorRed)
        self.duplicate_indicators(Indicador)
        self.assertEqual(12, IndicadorRed.objects.all().count())
        self.assertEqual(14, Indicador.objects.all().count())
        self.assertEqual(6, Indicador.objects.filter(jurisdiccion_id='test_1').count())
        call_command('delete_duplicated_indicators')
        self.assertEqual(6, IndicadorRed.objects.all().count())
        self.assertEqual(8, Indicador.objects.all().count())
        self.assertEqual(3, Indicador.objects.filter(jurisdiccion_id='test_1').count())

    def duplicate_indicators(self, model):
        for indicator in model.objects.all():
            indicator.id = None
            indicator.save()

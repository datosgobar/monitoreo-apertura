#! coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from django.test import TestCase
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from monitoreo.apps.dashboard.models import IndicatorType, TableColumn, IndicadorRed

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


class ColumnTest(TestCase):
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

        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED')

        IndicadorRed.objects.create(indicador_tipo=type_a, indicador_valor='42')
        IndicadorRed.objects.create(indicador_tipo=type_b, indicador_valor='[["d1", "l1"], ["d2", "l2"]]')
        IndicadorRed.objects.create(indicador_tipo=type_c, indicador_valor='{"k3":3, "k2": 1, "k1": 2}')

        # Necesario para agregar los indicadores con fecha distinta a la de hoy
        cls.past_date = parse_datetime('2000-01-01 12:00:00Z')

        old_a = IndicadorRed.objects.create(indicador_tipo=type_a, indicador_valor='23')
        old_b = IndicadorRed.objects.create(indicador_tipo=type_b, indicador_valor='[["d1", "l1"]]')
        old_c = IndicadorRed.objects.create(indicador_tipo=type_c, indicador_valor='{"k1": 1, "k2": 2, "k3":10}')

        old_ids = [indic.pk for indic in [old_a, old_b, old_c]]
        IndicadorRed.objects.filter(id__in=old_ids).update(fecha=cls.past_date)

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

#! coding: utf-8
from django.test import TestCase
from monitoreo.apps.dashboard.models import IndicatorType, TableColumn


class ColumnTest(TestCase):
    indicator_name = "Indicador test"
    indicator_full_name = "Nombre completo del indicador test"

    indicators_info = [{
        "indicador_nombre": indicator_name,
        "indicador_nombre_tabla": indicator_full_name
    }]

    def setUp(self):
        _type = IndicatorType(nombre=self.indicator_name, tipo="TEST")
        _type.save()

    def test_indicators_created(self):
        with self.settings(INDICATORS_INFO=self.indicators_info):
            column = TableColumn(
                indicator=IndicatorType.objects.get(nombre=self.indicator_name))
            column.clean()
            column.save()
            self.assertEqual(column.full_name, self.indicator_full_name)

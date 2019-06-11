import re

from django.test import TestCase

from monitoreo.apps.dashboard.custom_generators import custom_row_generator
from monitoreo.apps.dashboard.models import IndicatorType, IndicadorRed


class RowGeneratorTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED', resumen=True)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED', resumen=True,
                                              mostrar=False)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED', mostrar=False)

        types = [type_a, type_b, type_c, type_d, type_e]
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}', '100', '1']
        for t, v in zip(types, values):
            IndicadorRed.objects.create(indicador_tipo=t, indicador_valor=v)

    def setUp(self):
        self.fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
        self.rows_list = list(custom_row_generator())

    def test_generated_rows_are_not_empty(self):
        self.assertIsNotNone(self.rows_list)

    def test_first_generated_row_are_fieldnames(self):
        first_row = self.rows_list[0].split(',')
        first_row_contents = [row.strip() for row in first_row]
        self.assertEquals(self.fieldnames, first_row_contents)


    def test_dates_column_has_dates(self):
        data_rows = self.rows_list[1:]
        dates_column = [row.split(',')[0] for row in data_rows]

        for date in dates_column:
            matched_pattern = re.match("\d{4}-\d{2}-\d{2}", date)
            self.assertTrue(matched_pattern)

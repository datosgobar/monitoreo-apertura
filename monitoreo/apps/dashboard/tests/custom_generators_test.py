import datetime
import re

from django.test import TestCase

from monitoreo.apps.dashboard.custom_generators import custom_row_generator
from monitoreo.apps.dashboard.models import IndicatorType, IndicadorRed, Indicador, \
    IndicadorFederador


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
        self.indicador_red_headers = IndicadorRed.get_headers()
        self.indicador_red_rows_list = list(custom_row_generator(IndicadorRed))
        self.indicador_headers = Indicador.get_headers()
        self.indicador_rows_list = list(custom_row_generator(Indicador))
        self.indicador_federador_headers = IndicadorFederador.get_headers()
        self.indicador_federador_rows_list = list(custom_row_generator(IndicadorFederador))

    def test_generated_indicador_red_rows_are_not_empty(self):
        self.assertTrue(self.indicador_red_rows_list)

    def test_generated_indicador_rows_are_not_empty(self):
        self.assertTrue(self.indicador_rows_list)

    def test_generated_indicador_federador_rows_are_not_empty(self):
        self.assertTrue(self.indicador_federador_rows_list)

    def assert_first_row_is_header(self, model):
        header = model.get_headers()
        first_row = [row.strip() for row in list(custom_row_generator(model))[0].split(',')]
        self.assertEquals(first_row, header)

    def test_first_generated_row_are_headers(self):

        self.assert_first_row_is_header(IndicadorRed)
        self.assert_first_row_is_header(Indicador)
        self.assert_first_row_is_header(IndicadorFederador)

    def test_indicador_red_headers_is_the_same_as_fieldnames(self):
        first_row = self.indicador_red_rows_list[0].split(',')
        headers = [row.strip() for row in first_row]
        self.assertEquals(IndicadorRed.get_fieldnames(), headers)

    def test_indicador_headers_is_not_the_same_as_its_fieldnames(self):
        indicador_first_row = self.indicador_rows_list[0].split(',')
        indicador_headers = [row.strip() for row in indicador_first_row]
        self.assertNotEquals(Indicador.get_fieldnames(), indicador_headers)

    def indicador_federador_headers_is_not_the_same_as_its_fieldnames(self):
        indicador_federador_first_row = self.indicador_federador_rows_list[0].split(',')
        indicador_federador_headers = [row.strip() for row in indicador_federador_first_row]
        self.assertNotEquals(IndicadorFederador.get_fieldnames(), indicador_federador_headers)

    def test_dates_column_has_dates(self):
        data_rows = self.indicador_red_rows_list[1:]
        dates_column = [row.split(',')[0] for row in data_rows]

        for date in dates_column:
            matched_pattern = re.match("\d{4}-\d{2}-\d{2}", date)
            self.assertTrue(matched_pattern)

    def test_dates_column_contains_indicator_created_date(self):
        dates_column = [row.split(',')[0] for row in self.indicador_red_rows_list[1:]]
        current_date = datetime.date.today().strftime('%Y-%m-%d')

        for date in dates_column:
            self.assertEquals(current_date, date)

    def test_generator_rows_quantity_is_indicators_quantity(self):
        indicators_quantity = IndicadorRed.objects\
            .values('fecha', 'indicador_tipo__nombre', 'indicador_valor').count()
        data_rows_quantity = len(self.indicador_red_rows_list[1:])

        self.assertEquals(indicators_quantity, data_rows_quantity)

    def test_rows_contain_correct_value(self):
        first_data_row = self.indicador_red_rows_list[1].split(',')
        last_data_row = self.indicador_red_rows_list[-1].split(',')

        self.assertEquals('42', first_data_row[2].strip())
        self.assertEquals('1', last_data_row[2].strip())

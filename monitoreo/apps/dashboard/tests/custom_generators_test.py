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
        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='id1',
                                     jurisdiccion_nombre='nodo1')
        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        for t, v in zip(types, values):
            Indicador.objects.create(indicador_tipo=t, indicador_valor=v, jurisdiccion_id='id2',
                                     jurisdiccion_nombre='nodo2')

        values = ['23', '[["d2", "l2"]]', '{"k2": 1}', '2', '3']
        for t, v in zip(types, values):
            IndicadorFederador.objects.create(indicador_tipo=t, indicador_valor=v,
                                              jurisdiccion_id='harvest_id',
                                              jurisdiccion_nombre='harvest node')

    def setUp(self):
        self.indicador_red_fieldnames = \
            ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
        self.indicador_fieldnames = \
            ['fecha', 'indicador_tipo__nombre',
             'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
        self.indicador_federador_fieldnames = self.indicador_fieldnames

        self.indicador_red_headers = \
            ['fecha', 'indicador_nombre',
             'indicador_apertura', 'indicador_valor']
        self.indicador_red_rows_list = list(custom_row_generator(
            IndicadorRed, self.indicador_red_fieldnames))

        self.indicador_headers = \
            ['fecha', 'indicador_nombre', 'indicador_apertura',
             'indicador_valor', 'nodo_nombre', 'nodo_id']
        self.indicador_rows_list = list(custom_row_generator(
            Indicador, self.indicador_fieldnames))

        self.indicador_federador_headers = self.indicador_headers
        self.indicador_federador_rows_list = list(custom_row_generator(
            IndicadorFederador, self.indicador_federador_fieldnames))

    def test_generated_indicador_red_rows_are_not_empty(self):
        self.assertTrue(self.indicador_red_rows_list)

    def test_generated_indicador_rows_are_not_empty(self):
        self.assertTrue(self.indicador_rows_list)

    def test_generated_indicador_federador_rows_are_not_empty(self):
        self.assertTrue(self.indicador_federador_rows_list)

    def assert_first_row_is_header(self, model, fieldnames, headers):
        first_row = [row.strip() for row in list(custom_row_generator(model, fieldnames))[0].split(',')]
        self.assertEquals(first_row, headers)

    def test_first_generated_row_are_headers(self):
        self.assert_first_row_is_header(IndicadorRed, self.indicador_red_fieldnames, self.indicador_red_headers)
        self.assert_first_row_is_header(Indicador, self.indicador_fieldnames, self.indicador_headers)
        self.assert_first_row_is_header(IndicadorFederador, self.indicador_federador_fieldnames,
                                        self.indicador_federador_headers)

    def assert_dates_column_has_dates_format(self, model, fieldnames):
        data_rows = list(custom_row_generator(model, fieldnames))[1:]
        dates_column = [row.split(',')[0] for row in data_rows]

        for date in dates_column:
            matched_pattern = re.match("\d{4}-\d{2}-\d{2}", date)
            self.assertTrue(matched_pattern)

    def test_dates_column_has_dates(self):
        self.assert_dates_column_has_dates_format(IndicadorRed, self.indicador_red_fieldnames)
        self.assert_dates_column_has_dates_format(Indicador, self.indicador_fieldnames)
        self.assert_dates_column_has_dates_format(IndicadorFederador, self.indicador_federador_fieldnames)

    def assert_dates_column_contains_indicator_created_date(self, model, fieldnames):
        dates_column = [row.split(',')[0] for row in list(custom_row_generator(model, fieldnames))[1:]]
        current_date = datetime.date.today().strftime('%Y-%m-%d')

        for date in dates_column:
            self.assertEquals(current_date, date)

    def test_dates_column_contains_indicator_created_date(self):
        self.assert_dates_column_contains_indicator_created_date(IndicadorRed, self.indicador_red_fieldnames)
        self.assert_dates_column_contains_indicator_created_date(Indicador, self.indicador_fieldnames)
        self.assert_dates_column_contains_indicator_created_date(IndicadorFederador,
                                                                 self.indicador_federador_fieldnames)

    def assert_generated_rows_equals_indicator_count(self, model, fieldnames, count):
        data_rows_quantity = len(list(custom_row_generator(model, fieldnames))[1:])
        self.assertEquals(count, data_rows_quantity)

    def test_generated_rows_quantity_is_indicators_count(self):
        # Indicadores numéricos + listados + (multidimendsionales * amplitud de cada uno)
        self.assert_generated_rows_equals_indicator_count(IndicadorRed, self.indicador_red_fieldnames, 6)
        self.assert_generated_rows_equals_indicator_count(Indicador, self.indicador_fieldnames, 11)
        self.assert_generated_rows_equals_indicator_count(IndicadorFederador, self.indicador_federador_fieldnames, 5)

    def _data_row(self, indicators, idx):
        row = indicators[idx].split(',')
        row = list(map((lambda x: x.strip()), row))
        return row

    def test_indicador_red_rows_contain_correct_values(self):
        first_data_row = self._data_row(self.indicador_red_rows_list, 1)
        last_data_row = self._data_row(self.indicador_red_rows_list, -1)

        expected_first = ['2019-09-13', 'ind_a', 'completo', '42']
        expected_last = ['2019-09-13', 'ind_e', 'completo', '1']

        self.assertListEqual(expected_first, first_data_row)
        self.assertEquals(expected_last, last_data_row)

    def test_indicador_rows_contain_correct_values(self):
        first_data_row = self._data_row(self.indicador_rows_list, 1)
        last_data_row = self._data_row(self.indicador_rows_list, -1)
        expected_first = ['2019-09-13', 'ind_a', 'completo',
                          '23', 'nodo1', 'id1']
        expected_last = ['2019-09-13', 'ind_e', 'completo',
                         '2', 'nodo2', 'id2']

        self.assertListEqual(expected_first, first_data_row)
        self.assertEquals(expected_last, last_data_row)

    def test_indicador_federador_rows_contain_correct_values(self):
        first_data_row = self._data_row(self.indicador_federador_rows_list, 1)
        last_data_row = self._data_row(self.indicador_federador_rows_list, -1)
        expected_first = ['2019-09-13', 'ind_a', 'completo', '23',
                          'harvest node', 'harvest_id']
        expected_last = ['2019-09-13', 'ind_e', 'completo', '3',
                         'harvest node', 'harvest_id']

        self.assertListEqual(expected_first, first_data_row)
        self.assertEquals(expected_last, last_data_row)

    def test_network_indicators_spread_values(self):
        pass

    def test_node_indicators_spread_values(self):
        pass

    def test_federator_indicators_spread_values(self):
        pass

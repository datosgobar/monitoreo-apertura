import datetime
import re

from django.test import TestCase

from monitoreo.apps.dashboard.context_managers import suppress_autotime
from monitoreo.apps.dashboard.custom_generators import csv_panel_writer
from monitoreo.apps.dashboard.models import IndicatorType, IndicadorRed, Indicador, \
    IndicadorFederador


class RowGeneratorTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_date = datetime.date(year=2000, month=1, day=1)
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED', resumen=True)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED', resumen=True,
                                              mostrar=False)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED', mostrar=False)

        types = [type_a, type_b, type_c, type_d, type_e]
        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}', '100', '1']
        for t, v in zip(types, values):
            with suppress_autotime(IndicadorRed, ['fecha']):
                IndicadorRed.objects.create(indicador_tipo=t, indicador_valor=v,
                                            fecha=cls.test_date)
        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        for t, v in zip(types, values):
            with suppress_autotime(Indicador, ['fecha']):
                Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                         jurisdiccion_id='id1',
                                         jurisdiccion_nombre='nodo1',
                                         fecha=cls.test_date)
        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        for t, v in zip(types, values):
            with suppress_autotime(Indicador, ['fecha']):
                Indicador.objects.create(indicador_tipo=t, indicador_valor=v,
                                         jurisdiccion_id='id2',
                                         jurisdiccion_nombre='nodo2',
                                         fecha=cls.test_date)

        values = ['23', '[["d2", "l2"]]', '{"k2": 1}', '2', '3']
        for t, v in zip(types, values):
            with suppress_autotime(IndicadorFederador, ['fecha']):
                IndicadorFederador.objects.create(
                    indicador_tipo=t, indicador_valor=v,
                    jurisdiccion_id='harvest_id',
                    jurisdiccion_nombre='harvest node', fecha=cls.test_date)

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
        self.indicador_red_rows_list = list(csv_panel_writer(
            IndicadorRed, self.indicador_red_fieldnames))

        self.indicador_headers = \
            ['fecha', 'indicador_nombre', 'indicador_apertura',
             'indicador_valor', 'nodo_nombre', 'nodo_id']
        self.indicador_rows_list = list(csv_panel_writer(
            Indicador, self.indicador_fieldnames))

        self.indicador_federador_headers = self.indicador_headers
        self.indicador_federador_rows_list = list(csv_panel_writer(
            IndicadorFederador, self.indicador_federador_fieldnames))

    def test_generated_indicador_red_rows_are_not_empty(self):
        self.assertTrue(self.indicador_red_rows_list)

    def test_generated_indicador_rows_are_not_empty(self):
        self.assertTrue(self.indicador_rows_list)

    def test_generated_indicador_federador_rows_are_not_empty(self):
        self.assertTrue(self.indicador_federador_rows_list)

    def assert_first_row_is_header(self, model, fieldnames, headers):
        first_row = [row.strip() for row in list(csv_panel_writer(model, fieldnames))[0].split(',')]
        self.assertEquals(first_row, headers)

    def test_first_generated_row_are_headers(self):
        self.assert_first_row_is_header(IndicadorRed, self.indicador_red_fieldnames, self.indicador_red_headers)
        self.assert_first_row_is_header(Indicador, self.indicador_fieldnames, self.indicador_headers)
        self.assert_first_row_is_header(IndicadorFederador, self.indicador_federador_fieldnames,
                                        self.indicador_federador_headers)

    def assert_dates_column_has_dates_format(self, model, fieldnames):
        data_rows = list(csv_panel_writer(model, fieldnames))[1:]
        dates_column = [row.split(',')[0] for row in data_rows]

        for date in dates_column:
            matched_pattern = re.match("\d{4}-\d{2}-\d{2}", date)
            self.assertTrue(matched_pattern)

    def test_dates_column_has_dates(self):
        self.assert_dates_column_has_dates_format(IndicadorRed, self.indicador_red_fieldnames)
        self.assert_dates_column_has_dates_format(Indicador, self.indicador_fieldnames)
        self.assert_dates_column_has_dates_format(IndicadorFederador, self.indicador_federador_fieldnames)

    def assert_dates_column_contains_indicator_created_date(self, model, fieldnames):
        dates_column = [row.split(',')[0] for row in list(csv_panel_writer(model, fieldnames))[1:]]
        expected_date = '2000-01-01'

        for date in dates_column:
            self.assertEquals(expected_date, date)

    def test_dates_column_contains_indicator_created_date(self):
        self.assert_dates_column_contains_indicator_created_date(IndicadorRed, self.indicador_red_fieldnames)
        self.assert_dates_column_contains_indicator_created_date(Indicador, self.indicador_fieldnames)
        self.assert_dates_column_contains_indicator_created_date(IndicadorFederador,
                                                                 self.indicador_federador_fieldnames)

    def assert_generated_rows_equals_indicator_count(self, model, fieldnames, count):
        data_rows_quantity = len(list(csv_panel_writer(model, fieldnames))[1:])
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

        expected_first = ['2000-01-01', 'ind_a', 'completo', '42']
        expected_last = ['2000-01-01', 'ind_e', 'completo', '1']

        self.assertListEqual(expected_first, first_data_row)
        self.assertEquals(expected_last, last_data_row)

    def test_indicador_rows_contain_correct_values(self):
        first_data_row = self._data_row(self.indicador_rows_list, 1)
        last_data_row = self._data_row(self.indicador_rows_list, -1)
        expected_first = ['2000-01-01', 'ind_a', 'completo',
                          '23', 'nodo1', 'id1']
        expected_last = ['2000-01-01', 'ind_e', 'completo',
                         '2', 'nodo2', 'id2']

        self.assertListEqual(expected_first, first_data_row)
        self.assertEquals(expected_last, last_data_row)

    def test_indicador_federador_rows_contain_correct_values(self):
        first_data_row = self._data_row(self.indicador_federador_rows_list, 1)
        last_data_row = self._data_row(self.indicador_federador_rows_list, -1)
        expected_first = ['2000-01-01', 'ind_a', 'completo', '23',
                          'harvest node', 'harvest_id']
        expected_last = ['2000-01-01', 'ind_e', 'completo', '3',
                         'harvest node', 'harvest_id']

        self.assertListEqual(expected_first, first_data_row)
        self.assertEquals(expected_last, last_data_row)

    def test_network_indicators_spread_values(self):
        complete_data_row = self._data_row(self.indicador_red_rows_list, -2)
        spread_data_row = self._data_row(self.indicador_red_rows_list, 3)
        expected_complete = ['2000-01-01', 'ind_d', 'completo', '100']
        expected_spread = ['2000-01-01', 'ind_c', 'k1', '1']

        self.assertListEqual(expected_complete, complete_data_row)
        self.assertEquals(expected_spread, spread_data_row)

    def test_node_indicators_spread_values(self):
        complete_data_row = self._data_row(self.indicador_rows_list, -2)
        spread_data_row = self._data_row(self.indicador_rows_list, 3)
        expected_complete = ['2000-01-01', 'ind_d', 'completo', '50',
                             'nodo2', 'id2']
        expected_spread = ['2000-01-01', 'ind_c', 'k2', '1',
                           'nodo1', 'id1']

        self.assertListEqual(expected_complete, complete_data_row)
        self.assertEquals(expected_spread, spread_data_row)

    def test_federator_indicators_spread_values(self):
        complete_data_row = self._data_row(self.indicador_federador_rows_list, -2)
        spread_data_row = self._data_row(self.indicador_federador_rows_list, 3)
        expected_complete = ['2000-01-01', 'ind_d', 'completo', '2',
                             'harvest node', 'harvest_id']
        expected_spread = ['2000-01-01', 'ind_c', 'k2', '1',
                           'harvest node', 'harvest_id']

        self.assertListEqual(expected_complete, complete_data_row)
        self.assertEquals(expected_spread, spread_data_row)

    def test_network_csv_included_indicator_types(self):
        excluded_types = ('ind_a', 'ind_b', 'ind_c')
        IndicatorType.objects.filter(nombre__in=excluded_types).update(
            panel_red=False)
        for row in csv_panel_writer(
                IndicadorRed, self.indicador_red_fieldnames):
            for excluded_type in excluded_types:
                self.assertNotIn(excluded_type, row)

    def test_nodes_csv_included_indicator_types(self):
        excluded_types = ('ind_b', 'ind_d', 'ind_e')
        IndicatorType.objects.filter(nombre__in=excluded_types).update(
            panel_nodos=False)
        for row in csv_panel_writer(Indicador, self.indicador_fieldnames):
            for excluded_type in excluded_types:
                self.assertNotIn(excluded_type, row)

    def test_federators_csv_included_indicator_types(self):
        excluded_types = ('ind_c', 'ind_d', 'ind_e')
        IndicatorType.objects.filter(nombre__in=excluded_types).update(
            panel_federadores=False)
        for row in csv_panel_writer(
                IndicadorFederador, self.indicador_federador_fieldnames):
            for excluded_type in excluded_types:
                self.assertNotIn(excluded_type, row)

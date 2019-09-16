#! coding: utf-8
import csv
import datetime

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import localdate

from django_datajsonar.models import Node

from monitoreo.apps.dashboard.indicators_tasks import write_time_series_files
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, \
    IndicatorType, IndicadorFederador, HarvestingNode
from monitoreo.apps.dashboard.tests.test_utils.read_bytes_as_csv import read_content_as_csv


class ViewsTest(TestCase):
    def setUp(self):
        # set mock nodes
        self.node1 = Node.objects.create(catalog_id='id1', catalog_url='url',
                                         indexable=True)
        self.node2 = Node.objects.create(catalog_id='id2', catalog_url='url',
                                         indexable=True)

        self.harvest_node = HarvestingNode.objects.create(
            catalog_id='idx1',
            name='index1',
            url='http://datos.test.ar',
            apikey='apikey',
            enabled=True)

        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED',
                                              series_nodos=False)
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED',
                                              resumen=True, series_red=False,
                                              series_nodos=False,
                                              series_federadores=False)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED',
                                              resumen=True, mostrar=False,
                                              series_red=False,
                                              series_federadores=False)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED',
                                              mostrar=False)

        types = [type_a, type_b, type_c, type_d, type_e]

        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}',
                  '100', '1']
        self._create_indicators(types, values)

        # Necesario para agregar los indicadores con fecha distinta a la de hoy
        values = ['23', '[["d1", "l1"]]', '{"k1":1, "k2": 2, "k3": 10}',
                  '50', '0']
        old_ids = self._create_indicators(types, values)

        self.past_date = localdate() - datetime.timedelta(days=2)
        IndicadorRed.objects.filter(id__in=old_ids).update(
            fecha=self.past_date)

        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        self._create_indicators(types, values, node_id='id1', node_name='nodo1')

        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        self._create_indicators(types, values, node_id='id2', node_name='nodo2')

        values = ['21', '[["d1", "l1"]]', '{"k2": 1}', '200', '4']
        self._create_indicators(types, values, node_id='idx1',
                                node_name='index1', harvesting=True)

        write_time_series_files()

    def _create_indicators(self, ind_type, values,
                           node_id=None, node_name='', harvesting=False):
        res = []
        for ind_type, value in zip(ind_type, values):
            if node_id is None:
                created = IndicadorRed.objects.create(
                    indicador_tipo=ind_type, indicador_valor=value)
            elif harvesting:
                created = IndicadorFederador.objects.create(
                    indicador_tipo=ind_type, indicador_valor=value,
                    jurisdiccion_id=node_id, jurisdiccion_nombre=node_name)
            else:
                created = Indicador.objects.create(
                    indicador_tipo=ind_type, indicador_valor=value,
                    jurisdiccion_id=node_id, jurisdiccion_nombre=node_name)
            res.append(created.id)

        return res

    def _format_previous_dates(self, delta):
        return (localdate() - datetime.timedelta(days=delta))\
            .strftime('%Y-%m-%d')

    def test_series_headers(self):
        network_response = Client().get(reverse('admin:network_series'))
        expected_disposition =\
            'attachment; filename="series-indicadores-red.csv"'
        self.assertEqual(expected_disposition,
                         network_response['Content-Disposition'])

        node_response = Client().get(reverse('admin:node_series',
                                             kwargs={'node_id': 'id1'}))
        expected_disposition = \
            'attachment; filename="series-indicadores-id1.csv"'
        self.assertEqual(expected_disposition,
                         node_response['Content-Disposition'])

    def test_series_header(self):
        network_response = Client().get(reverse('admin:network_series'))
        series = read_content_as_csv(network_response.content)

        expected_headers = ['indice_tiempo', 'ind_a', 'ind_b', 'ind_e']
        headers = next(series, None)
        self.assertListEqual(expected_headers, headers)

    def test_header_respects_indicator_type_order(self):
        type_a = IndicatorType.objects.get(nombre='ind_a')
        type_e = IndicatorType.objects.filter(nombre='ind_e')
        type_a.swap(type_e)

        network_response = Client().get(reverse('admin:network_series'))
        series = read_content_as_csv(network_response.content)
        expected_headers = ['indice_tiempo', 'ind_e', 'ind_b', 'ind_a']
        headers = next(series, None)
        self.assertEqual(expected_headers, headers)

    def test_series_rows(self):
        network_response = Client().get(reverse('admin:network_series'))
        series = network_response.content.decode('utf-8').splitlines()
        series_csv = csv.DictReader(series)
        two_days_ago = self._format_previous_dates(2)
        expected_row = {'indice_tiempo': two_days_ago,
                        'ind_a': '23',
                        'ind_b': '',
                        'ind_e': '0'}
        row = next(series_csv, None)
        self.assertDictEqual(expected_row, row)
        yesterday = self._format_previous_dates(1)
        expected_row = {'indice_tiempo': yesterday,
                        'ind_a': '',
                        'ind_b': '',
                        'ind_e': ''}
        row = next(series_csv, None)
        self.assertDictEqual(expected_row, row)
        today = self._format_previous_dates(0)
        expected_row = {'indice_tiempo': today,
                        'ind_a': '42',
                        'ind_b': '',
                        'ind_e': '1'}
        row = next(series_csv, None)
        self.assertDictEqual(expected_row, row)

    def test_node_series(self):
        node_response = Client().get(reverse('admin:node_series',
                                             kwargs={'node_id': 'id1'}))
        series = node_response.content.decode('utf-8').splitlines()
        self.assertEqual(2, len(series))
        series_csv = csv.DictReader(series)
        today = self._format_previous_dates(0)
        expected_row = {'indice_tiempo': today,
                        'ind_a': '23',
                        'ind_d': '500',
                        'ind_e': '2'}
        row = next(series_csv, None)
        self.assertDictEqual(expected_row, row)

    def test_indexing_series(self):
        node_response = Client().get(reverse('admin:indexing_series',
                                             kwargs={'node_id': 'idx1'}))
        series = node_response.content.decode('utf-8').splitlines()
        self.assertEqual(2, len(series))
        series_csv = csv.DictReader(series)
        today = self._format_previous_dates(0)
        expected_row = {'indice_tiempo': today,
                        'ind_a': '21',
                        'ind_b': '',
                        'ind_e': '4'}
        row = next(series_csv, None)
        self.assertDictEqual(expected_row, row)

    def assert_not_empty_and_has_content_in_rows(self, model, response):
        indicators_contents_as_string = []
        for content in response.streaming_content:
            indicators_contents_as_string.append(content.decode('utf-8'))

        rows_quantity = 0
        indicators = csv.DictReader(indicators_contents_as_string)
        for row in indicators:
            rows_quantity += 1
            self.assertIsNotNone(row)

    def test_networks_indicators_csvs_are_not_empty_and_have_all_models_as_rows(self):
        network_response = self.client.get(reverse('dashboard:indicadores-red-csv'))
        self.assert_not_empty_and_has_content_in_rows(IndicadorRed, network_response)

    def test_node_indicators_csvs_are_not_empty_and_have_all_models_as_rows(self):
        node_response = self.client.get(reverse('dashboard:indicadores-nodo-csv'))
        self.assert_not_empty_and_has_content_in_rows(Indicador, node_response)

    def test_federator_indicators_csvs_are_not_empty_and_have_all_models_as_rows(self):
        federator_response = self.client.get(reverse('dashboard:indicadores-federadores-csv'))
        self.assert_not_empty_and_has_content_in_rows(IndicadorFederador, federator_response)

    def test_network_indicators_series_response(self):
        network_response = self.client.get(reverse('dashboard:indicadores-red-series'))
        self.assertEqual(200, network_response.status_code)
        self.assertEqual('text/csv',
                         network_response._headers['content-type'][1])
        self.assertEqual('attachment; filename=indicadores-red-nodos-series.csv',
                         network_response._headers['content-disposition'][1])

    def test_node_indicators_series_response(self):
        nodes_response = self.client.get(
            reverse('dashboard:indicadores-nodos-series',
                    args=['indicadores-id1-series.csv']))
        self.assertEqual(200, nodes_response.status_code)
        self.assertEqual('text/csv',
                         nodes_response._headers['content-type'][1])
        self.assertEqual('attachment; filename=indicadores-id1-series.csv',
                         nodes_response._headers['content-disposition'][1])

    def test_federator_indicators_series_response(self):
        federator_response = self.client.get(
            reverse('dashboard:indicadores-federadores-series',
                    args=['indicadores-idx1-series.csv']))
        self.assertEqual(200, federator_response.status_code)
        self.assertEqual('text/csv',
                         federator_response._headers['content-type'][1])
        self.assertEqual('attachment; filename=indicadores-idx1-series.csv',
                         federator_response._headers['content-disposition'][1])

    def test_non_existant_nodes_indicators_series_response(self):
        fail_response = self.client.get(
            reverse('dashboard:indicadores-nodos-series',
                    args=['indicadores-null-series.csv']))
        self.assertEqual(400, fail_response.status_code)

    def test_non_existant_federator_indicators_series_response(self):
        fail_response = self.client.get(
            reverse('dashboard:indicadores-federadores-series',
                    args=['indicadores-null-series.csv']))
        self.assertEqual(400, fail_response.status_code)

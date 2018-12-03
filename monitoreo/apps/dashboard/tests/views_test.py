#! coding: utf-8
import csv
import datetime

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.timezone import localdate

from django_datajsonar.models import Node

from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, IndicatorType


class ViewsTest(TestCase):
    def setUp(self):
        # set mock nodes
        self.node1 = Node.objects.create(catalog_id='id1', catalog_url='url',
                                         indexable=True)
        self.node2 = Node.objects.create(catalog_id='id2', catalog_url='url',
                                         indexable=True)

        # set mock indicators
        type_a = IndicatorType.objects.create(nombre='ind_a', tipo='RED')
        type_b = IndicatorType.objects.create(nombre='ind_b', tipo='RED')
        type_c = IndicatorType.objects.create(nombre='ind_c', tipo='RED',
                                              resumen=True, series=False)
        type_d = IndicatorType.objects.create(nombre='ind_d', tipo='RED',
                                              resumen=True, mostrar=False,
                                              series=False)
        type_e = IndicatorType.objects.create(nombre='ind_e', tipo='RED',
                                              mostrar=False)

        types = [type_a, type_b, type_c, type_d, type_e]

        values = ['42', '[["d1", "l1"], ["d2", "l2"]]', '{"k1": 1, "k2": 2}',
                  '100', '1']
        self._create_indicators(types, values)

        values = ['23', '[["d1", "l1"]]', '{"k2": 1}', '500', '2']
        self._create_indicators(types, values, node_id='id1', node_name='nodo1')

        values = ['19', '[["d2", "l2"]]', '{"k1": 1, "k2": 1}', '50', '2']
        self._create_indicators(types, values, node_id='id2', node_name='nodo2')

        # Necesario para agregar los indicadores con fecha distinta a la de hoy
        values = ['23', '[["d1", "l1"]]', '{"k1":1, "k2": 2, "k3": 10}',
                  '50', '0']
        old_ids = self._create_indicators(types, values)

        self.past_date = localdate() - datetime.timedelta(days=2)
        IndicadorRed.objects.filter(id__in=old_ids).update(
            fecha=self.past_date)

    def _create_indicators(self, ind_type, values, node_id=None, node_name=''):
        res = []
        for ind_type, value in zip(ind_type, values):
            if node_id and node_name:
                created = Indicador.objects.create(
                    indicador_tipo=ind_type, indicador_valor=value,
                    jurisdiccion_id=node_id, jurisdiccion_nombre=node_name)
            else:
                created = IndicadorRed.objects.create(
                    indicador_tipo=ind_type, indicador_valor=value)
            res.append(created.id)

        return res

    def _format_previous_dates(self, delta):
        return (localdate() - datetime.timedelta(days=delta))\
            .strftime('%Y-%m-%d')

    def test_landing_with_no_indicators_loaded_returns_500(self):
        IndicadorRed.objects.all().delete()
        response = Client().get(reverse('dashboard:landing'))
        self.assertEqual(response.status_code, 500)

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
        series = csv.reader(network_response.content.splitlines())
        expected_headers = {'indice_tiempo', 'ind_a', 'ind_b', 'ind_e'}
        headers = next(series, None)
        self.assertSetEqual(expected_headers, set(headers))

    def test_series_rows(self):
        network_response = Client().get(reverse('admin:network_series'))
        series = network_response.content.splitlines()
        self.assertEqual(4, len(series))
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
        series = node_response.content.splitlines()
        self.assertEqual(2, len(series))
        series_csv = csv.DictReader(series)
        today = self._format_previous_dates(0)
        expected_row = {'indice_tiempo': today,
                        'ind_a': '23',
                        'ind_b': '',
                        'ind_e': '2'}
        row = next(series_csv, None)
        self.assertDictEqual(expected_row, row)

#! coding: utf-8
import json
from django.test import TestCase
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed
from monitoreo.apps.dashboard.helpers import load_catalogs
from pydatajson import DataJson
from django.core.management import call_command


class CommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('indicadores')

        url = "https://raw.githubusercontent.com/datosgobar/libreria" \
              "-catalogos/master/"
        central = url + 'datosgobar/data.json'
        cls.catalogs = load_catalogs(url)
        cls.indicators, cls.network_indicators = \
            DataJson().generate_catalogs_indicators(cls.catalogs, central)
        cls.dj = DataJson()

    def test_indicators_created(self):
        self.assertTrue(Indicador.objects.all())

    def test_network_indicators_created(self):
        self.assertTrue(IndicadorRed.objects.all())

    def test_verify_network_indicators(self):
        for network_indicator in IndicadorRed.objects.all():
            indicator_name = network_indicator.indicador_tipo.nombre
            self.assertEqual(json.loads(network_indicator.indicador_valor),
                             self.network_indicators[indicator_name])

    def test_verify_individual_indicators(self):
        for catalog in self.catalogs:
            # Obtengo los indicadores calculados directamente con DataJson
            catalog_index = self.catalogs.index(catalog)
            calculated_indicators = self.indicators[catalog_index]

            # Obtengo el nombre para filtrar los indicadores calculados con
            # el management command de ese catálogo
            validation = self.dj.validate_catalog(catalog)
            catalog_name = validation['error']['catalog']['title']
            indics = Indicador.objects.filter(catalogo_nombre=catalog_name)
            for indicator in indics:
                name = indicator.indicador_tipo.nombre
                self.assertEqual(json.loads(indicator.indicador_valor),
                                 calculated_indicators[name])

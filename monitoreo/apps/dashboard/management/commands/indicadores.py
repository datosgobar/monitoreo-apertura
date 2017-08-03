# coding=utf-8
from __future__ import unicode_literals
import json
from django.db.utils import DataError
from django.conf import settings
from django.core.management.base import BaseCommand
from pydatajson import DataJson

from indicadores_pad.indicators import PADIndicators
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, \
    IndicatorType, TableColumn
from monitoreo.apps.dashboard.helpers import load_catalogs
URL = "https://raw.githubusercontent.com/datosgobar/libreria-catalogos/master/"
CENTRAL = URL + 'datosgobar/data.json'

SPREADSHEET = '1z2itUsUxgty61AnB-09pxRQxbequLzEbWDragbZaHJs'


class Command(BaseCommand):
    help = """Calcula indicadores de la red de nodos del PAD de la república
    Argentina. Los catálogos son automáticamente leído de su librería remota,
    con raíz en https://www.github.com/datosgobar/libreria-catalogos"""

    def handle(self, *args, **options):
        data_json = DataJson()
        catalogs = load_catalogs(URL)
        indics, network_indics = data_json.generate_catalogs_indicators(
            catalogs,
            CENTRAL)
        names = []
        for catalog in catalogs:
            # Obtengo el nombre de los catálogos a partir de la validación
            validation = data_json.validate_catalog(catalog)
            catalog_name = validation['error']['catalog']['title']
            names.append(catalog_name)

        self.save_indicators(indics, names)
        self.save_network_indics(network_indics, 'RED')

        self.pad_indicators()

        # Creo columnas default si no existen
        if not TableColumn.objects.count():
            self.init_columns()

    def pad_indicators(self):
        pad = PADIndicators()
        indicators, network_indics = pad.generate_pad_indicators(SPREADSHEET)
        count = 0
        for jurisdiction, indics in indicators.items():
            for indic_name, value in indics.items():
                indic_type = IndicatorType.objects.get_or_create(
                    nombre=indic_name,
                    tipo='PAD')[0]
                indicador = Indicador(indicador_tipo=indic_type,
                                      indicador_valor=json.dumps(value),
                                      jurisdiccion_nombre=jurisdiction)
                indicador.save()
                count += 1

        self.stderr.write(u'Calculados indicadores del PAD')

        self.save_network_indics(network_indics, 'PAD')

    def save_network_indics(self, network_indics, indic_class):
        # Itero sobre los indicadores de red, creando modelos y agregándolos
        # a 'network_indicators'
        for indic_name, value in network_indics.items():
            indic_type = IndicatorType.objects.get_or_create(
                nombre=indic_name,
                tipo=indic_class)[0]
            network_indic = IndicadorRed(indicador_tipo=indic_type,
                                         indicador_valor=json.dumps(value))

            # Al ser los indicadores de red en cantidad reducida comparado con
            # la cantidad de los indicadores comunes, los guardo
            # uno por uno sin mayor impacto de performance
            network_indic.save()

        self.stderr.write(u'Calculados {} indicadores de red'.format(
            len(network_indics)
        ))

    def save_indicators(self, indics_list, names):
        """Crea modelos de Django a partir de cada indicador, y los guarda.
        Los nombres de los catálogos son leídos a partir de una lista 'names',
        con los indicadores y los nombres ordenados de la misma manera"""

        indic_models = 0  # Lista con todos los indicadores generados
        for indicators in indics_list:
            catalog_name = names[indics_list.index(indicators)]
            if not catalog_name:  # Fallback en caso de catálogos muy erróneos
                catalog_name = "Catálogo sin nombre"

            # Itero sobre los indicadores calculados, creando modelos y
            # agregándolos a la lista 'indicators'
            for indic_name, value in indicators.items():

                indic_type = IndicatorType.objects.get_or_create(
                    nombre=indic_name,
                    tipo='RED')[0]
                indic = Indicador(jurisdiccion_nombre=catalog_name,
                                  indicador_tipo=indic_type,
                                  indicador_valor=json.dumps(value))
                indic_models += 1
                try:
                    indic.save()
                except DataError:
                    self.stderr.write("Error guardando indicador: {0} - {1}: "
                                      "{2}".format(catalog_name,
                                                   indic_type,
                                                   json.dumps(value)))

        self.stderr.write(u'Calculados {0} indicadores en {1} catálogos'.format(
            indic_models, len(indics_list)))

    @staticmethod
    def init_columns():
        """ Inicializa las columnas de las tablas de indicadores a partir de
        valores predeterminados en la configuración de la aplicación
        """
        for indicator_name in settings.DEFAULT_INDICATORS:
            indicator = IndicatorType.objects.get(nombre=indicator_name)
            column = TableColumn(indicator=indicator)
            column.save()

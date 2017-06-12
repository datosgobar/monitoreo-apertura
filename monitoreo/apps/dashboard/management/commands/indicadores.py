# coding=utf-8
from __future__ import unicode_literals
import json
import requests
from urllib2 import urlopen
import yaml
from pydatajson import DataJson
from django.core.management.base import BaseCommand
from ...models import Indicador, IndicadorRed, IndicatorType
URL = "https://raw.githubusercontent.com/datosgobar/libreria-catalogos/master/"
INDEX_URL = URL + "indice.yml"
CENTRAL = URL + 'datosgobar/data.json'


class Command(BaseCommand):
    help = """Calcula indicadores de la red de nodos del PAD de la república
    Argentina. Los catálogos son automáticamente leído de su librería remota,
    con raíz en https://www.github.com/datosgobar/libreria-catalogos"""

    def handle(self, *args, **options):
        data_json = DataJson()
        catalogs = Command.load_catalogs()
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
        self.save_network_indics(network_indics)

    def save_network_indics(self, network_indics):
        # Itero sobre los indicadores de red, creando modelos y agregándolos
        # a 'network_indicators'
        for indic_name, value in network_indics.items():
            indic_type = IndicatorType.objects.get_or_create(
                nombre=indic_name)[0]
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
        indic_models = []  # Lista con todos los indicadores generados
        for indicators in indics_list:
            catalog_name = names[indics_list.index(indicators)]

            # Itero sobre los indicadores calculados, creando modelos y
            # agregándolos a la lista 'indicators'
            for indic_name, value in indicators.items():
                indic_type = IndicatorType.objects.get_or_create(
                    nombre=indic_name)[0]
                indic = Indicador(catalogo_nombre=catalog_name,
                                  indicador_tipo=indic_type,
                                  indicador_valor=json.dumps(value))
                indic_models.append(indic)

        # Guardo en la base de datos
        Indicador.objects.bulk_create(indic_models)
        self.stderr.write(u'Calculados {0} indicadores en {1} catálogos'.format(
            len(indic_models), len(indics_list)))

    @staticmethod
    def load_catalogs():
        """Lee el archivo 'indice.yml' en el directorio raíz, y devuelve una
        lista de URLs con rutas a los data.json de los catálogos marcados como
        "federados" en el índice. Se asume que los data.json siguen una ruta
        del tipo "<nombre-catalogo>/data.json"
        """
        catalogs = []

        yml_file = urlopen(INDEX_URL)
        catalogs_yaml = yaml.load(yml_file.read())
        for catalog_name, values in catalogs_yaml.items():
            if values.get('federado'):
                url = URL + catalog_name + '/data.json'
                try:
                    datajson = json.loads(urlopen(url).read())
                except:
                    continue
                catalogs.append(datajson)

        return catalogs

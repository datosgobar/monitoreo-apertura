#! coding: utf-8
import json
from urllib2 import urlopen, HTTPError

import yaml
from django.db.models import QuerySet


def fetch_latest_indicadors(indicators):
    """A partir de un QuerySet de todos los indicadores, devuelve un conjunto
    con todos los últimos (más recientes) indicadores de cada tipo.
    
    args:
        indicators (QuerySet): QuerySet con todos los modelos a ordenar por
            su campo 'fecha' (de tipo DateTimeField)
    returns:
        dict: conjunto iterable de python con todos los indicadores más 
        recientes como valores, y los nombres como claves
    """
    indicators = indicators.order_by('-fecha')
    latest = {}
    for i in indicators:
        if i.indicador_tipo.nombre not in latest:
            latest[i.indicador_tipo.nombre] = i.indicador_valor
    return latest


def load_catalogs(root_url):
    """Lee el archivo 'indice.yml' en el directorio raíz, recolecta las
    rutas a los data.json, las lee y parsea a diccionarios. Devuelve una
    lista con los diccionarios parseados.
    Se asume que los data.json siguen una ruta del tipo
    "root_url/<nombre-catalogo>/data.json"
    Args:
        root_url (str): URL al directorio raíz de la librería de catálogos
    """
    index_url = root_url + 'indice.yml'
    catalogs = []

    yml_file = urlopen(index_url)
    catalogs_yaml = yaml.load(yml_file.read())
    for catalog_name, values in catalogs_yaml.items():
        if values.get('federado'):
            url = root_url + catalog_name + '/data.json'
            # Intento parsear el documento, si falla, lo ignoro
            try:
                datajson = json.loads(urlopen(url).read())
            except (HTTPError, ValueError):
                continue
            catalogs.append(datajson)

    return catalogs

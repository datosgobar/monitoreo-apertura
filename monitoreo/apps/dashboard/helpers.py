#! coding: utf-8
import json
from urllib2 import urlopen, HTTPError
from six import text_type
import yaml

from .strings import ERRORS_DIVIDER


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
    indicators = indicators.order_by('-fecha', '-id')
    latest = {}
    for i in indicators:
        if i.indicador_tipo.nombre not in latest:
            if isinstance(i.indicador_valor, (str, unicode)):
                latest[i.indicador_tipo.nombre] = i.indicador_valor
            else:
                latest[i.indicador_tipo.nombre] = json.loads(str(i.indicador_valor))
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


def append_federation_errors(msg, errors):
    msg += ERRORS_DIVIDER.format(u'FEDERACIÓN')
    for dataset in errors:
        msg += dataset+u": "+errors[dataset]+u"\n"
    return msg


def append_validation_errors(msg, validation):
    msg += ERRORS_DIVIDER.format(u'VALIDACIÓN')
    if validation['error']['catalog']['status'] == 'ERROR':
        msg += u"Errores de catalogo: \n"
        msg = list_errors(msg, validation['error']['catalog']['errors'])

    for dataset in validation['error']['dataset']:
        msg += u"Errores en el dataset: {} \n".format(dataset['identifier'])
        msg = list_errors(msg, dataset['errors'])
    return msg


def list_errors(msg, errors):
    for error in errors:
        msg += u'\t {}: {} \n'.format(text_type(error['path']), error['message'])
    return msg

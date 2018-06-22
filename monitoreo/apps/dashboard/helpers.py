#! coding: utf-8
import json
from urllib2 import urlopen, HTTPError
from six import text_type
import yaml
from django_datajsonar.models import Dataset

from .strings import OVERALL_ASSESSMENT, VALIDATION_ERRORS, MISSING, HARVESTING_ERRORS, ERRORS_DIVIDER


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


def generate_task_log(catalog, catalog_id, invalid, missing, harvested_ids, federation_errors):
    validation = catalog.validate_catalog(only_errors=True)
    total = Dataset.objects.filter(indexable=True, catalog__identifier=catalog_id).count()
    log = OVERALL_ASSESSMENT.format(len(harvested_ids), total)
    if invalid:
        log += VALIDATION_ERRORS.format(len(invalid), list(invalid))

    if missing:
        log += MISSING.format(len(missing), list(missing))

    if federation_errors:
        log += HARVESTING_ERRORS.format(len(federation_errors.keys()), list(federation_errors.keys()))
        log = append_federation_errors(log, federation_errors)

    if validation['status'] == 'ERROR':
        # Separado del "if invalid", porque generar ids de distribuciones puede ocultar errores
        log = append_validation_errors(log, validation)

    return log


def append_federation_errors(log, errors):
    log += ERRORS_DIVIDER.format(u'FEDERACIÓN')
    for dataset in errors:
        log += dataset + u": " + errors[dataset] + u"\n"
    return log


def append_validation_errors(log, validation):
    log += ERRORS_DIVIDER.format(u'VALIDACIÓN')
    if validation['error']['catalog']['status'] == 'ERROR':
        log += u"Errores de catalogo: \n"
        log = list_errors(log, validation['error']['catalog']['errors'])

    for dataset in validation['error']['dataset']:
        log += u"Errores en el dataset: {} \n".format(dataset['identifier'])
        log = list_errors(log, dataset['errors'])
    return log


def list_errors(msg, errors):
    for error in errors:
        msg += u'\t {}: {} \n'.format(text_type(error['path']), error['message'])
    return msg

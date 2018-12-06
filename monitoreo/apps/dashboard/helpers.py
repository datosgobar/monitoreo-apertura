#! coding: utf-8
import json
import csv
import datetime

from six import text_type
from pydatajson import DataJson

from django.http import HttpResponse

from django_datajsonar.models import Dataset, Node

from .models import IndicatorsGenerationTask, IndicatorType
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


def load_catalogs(task):
    nodes = Node.objects.filter(indexable=True)
    catalogs = []
    for node in nodes:
        try:
            catalog = DataJson(node.catalog_url)
        except Exception as e:
            msg = u'Error accediendo al catálogo {}: {}'.format(node.catalog_id, str(e))
            IndicatorsGenerationTask.info(task, msg)
            continue

        catalog['identifier'] = node.catalog_id
        catalogs.append(catalog)
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


def download_time_series(indicators, node_id=None):
    response = HttpResponse(content_type='text/csv')
    filename = 'series-indicadores-{}.csv'.format(node_id or 'red')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return generate_time_series(indicators, response, node_id is None)


def generate_time_series(indicators, output, aggregated=False):
    dates = indicators.keys()
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        date_range = [min_date + datetime.timedelta(days=x) for x in
                      range(0, (max_date - min_date).days + 1)]
    else:
        date_range = []

    if aggregated:
        ind_types = IndicatorType.objects.filter(series_red=True)
    else:
        ind_types = IndicatorType.objects.filter(series_nodos=True)

    columns = list(ind_types.values_list('nombre', flat=True))
    fieldnames = ['indice_tiempo']
    fieldnames = fieldnames + columns

    writer = csv.DictWriter(output, fieldnames, extrasaction='ignore')
    writer.writeheader()
    for date in date_range:
        indicators.setdefault(date, {})
        indicators[date].update({'indice_tiempo': date})
        writer.writerow(indicators[date])
    return output

#! coding: utf-8
import csv
import datetime

from urllib.parse import urljoin
from six import text_type
from pydatajson import DataJson

from django.http import HttpResponse

from django_datajsonar.models import Dataset, Catalog, Node
from .models import IndicatorsGenerationTask, IndicatorType
from .strings import OVERALL_ASSESSMENT, VALIDATION_ERRORS, MISSING, HARVESTING_ERRORS, ERRORS_DIVIDER


def load_catalogs(task, nodes, harvesting=False):
    catalogs = []
    for node in nodes:
        try:
            if harvesting:
                url = urljoin(node.url, 'data.json')
                catalog = DataJson(url)
            else:
                catalog = DataJson(node.catalog_url,
                                   catalog_format=node.catalog_format,
                                   verify_ssl=node.verify_ssl)
        except Exception as e:
            msg = f'Error accediendo al catálogo {node.catalog_id}: {str(e)}'
            IndicatorsGenerationTask.info(task, msg)
            continue

        catalog['identifier'] = node.catalog_id
        catalogs.append(catalog)
    return catalogs


def generate_task_log(catalog, catalog_id, invalid, missing, harvested_ids, federation_errors):
    validation = catalog.validate_catalog(only_errors=True)
    indexable_datasets = Dataset.objects.filter(indexable=True, catalog__identifier=catalog_id)
    total = indexable_datasets.count()
    present = indexable_datasets.filter(present=True).count()
    log = OVERALL_ASSESSMENT.format(len(harvested_ids), present, total)
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
    log += ERRORS_DIVIDER.format('FEDERACIÓN')
    for dataset in errors:
        log += f"{dataset}: {errors[dataset]}\n"
    return log


def append_validation_errors(log, validation):
    log += ERRORS_DIVIDER.format('VALIDACIÓN')
    if validation['error']['catalog']['status'] == 'ERROR':
        log += "Errores de catalogo: \n"
        log = list_errors(log, validation['error']['catalog']['errors'])

    for dataset in validation['error']['dataset']:
        log += f"Errores en el dataset: {dataset['identifier']} \n"
        log = list_errors(log, dataset['errors'])
    return log


def list_errors(msg, errors):
    for error in errors:
        msg += f"\t {text_type(error['path'])}: {error['message']} \n"
    return msg


def download_time_series(indicators_queryset, node_id=None):
    response = HttpResponse(content_type='text/csv')
    filename = f"series-indicadores-{node_id or 'red'}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return generate_time_series(indicators_queryset, response)


def generate_time_series(indicators_queryset, output):
    indicators_table = indicators_queryset.numerical_indicators_by_date()
    dates = indicators_table.keys()
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        date_range = [min_date + datetime.timedelta(days=x) for x in
                      range(0, (max_date - min_date).days + 1)]
    else:
        date_range = []

    ind_types = indicators_queryset\
        .values_list('indicador_tipo__id', flat=True).distinct()
    fieldnames = ['indice_tiempo']
    columns = IndicatorType.objects.filter(id__in=ind_types).order_by('order')\
        .values_list('nombre', flat=True)
    columns = list(columns)
    fieldnames = fieldnames + columns

    writer = csv.DictWriter(output, fieldnames, extrasaction='ignore')
    writer.writeheader()
    for date in date_range:
        indicators_table.setdefault(date, {})
        indicators_table[date].update({'indice_tiempo': date})
        writer.writerow(indicators_table[date])
    return output


def get_datasets_for_node(node, datasets):
    catalog = Catalog.objects.get(identifier=node.catalog_id)
    datasets_in_node = [dataset for dataset in catalog.dataset_set.all()
                        if dataset in datasets]
    return datasets_in_node


def create_node_and_dataset_pairs(datasets):
    nodes_and_datasets_pairs = []
    catalog_identifiers = [dataset.catalog.identifier for dataset in datasets]
    nodes_to_report = Node.objects.filter(catalog_id__in=catalog_identifiers)

    for node in nodes_to_report:
        datasets_in_node = get_datasets_for_node(node, datasets)
        nodes_and_datasets_pairs.append((node, datasets_in_node))

    return nodes_and_datasets_pairs

#! coding: utf-8

import json
from django_rq import job

from pydatajson.core import DataJson
from pydatajson.federation import harvest_catalog_to_ckan
from django_datajsonar.models import Node, Dataset
from .helpers import append_federation_errors, append_validation_errors
from .models import HarvestingNode, FederationTask
from .strings import UNREACHABLE_CATALOG, OVERALL_ASSESSMENT, VALIDATION_ERRORS,\
    MISSING, HARVESTING_ERRORS, TASK_ERROR


def federation_run():
    harvesting_nodes = HarvestingNode.objects.filter(enabled=True)
    for harvester in harvesting_nodes:
        task = FederationTask.objects.create()
        portal_url = harvester.url
        apikey = harvester.apikey
        federate_catalogs(portal_url, apikey, task)


@job('indexing')
def federate_catalogs(portal_url, apikey, task):
    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        federate_catalog.delay(node, portal_url, apikey, task.pk)


@job('indexing', timeout=1800)
def federate_catalog(node, portal_url, apikey, task_id):
    task = FederationTask.objects.get(pk=task_id)
    catalog = get_catalog_from_node(node)
    catalog_id = node.catalog_id
    total = Dataset.objects.filter(indexable=True, catalog__identifier=catalog_id).count()
    msg = u"Catálogo: %s\n" % node.catalog_id
    if not catalog:
        msg += UNREACHABLE_CATALOG.format(node.catalog_id)
        FederationTask.info(task, msg)
        raise Exception(msg)
    validation = catalog.validate_catalog(only_errors=True)
    catalog.generate_distribution_ids()
    valid, invalid, missing = sort_datasets_by_condition(node, catalog)

    try:
        harvested_ids, federation_errors = harvest_catalog_to_ckan(catalog, portal_url, apikey, catalog_id, list(valid))
        msg += OVERALL_ASSESSMENT .format(len(harvested_ids), total)
        if invalid:
            msg += VALIDATION_ERRORS.format(len(invalid), list(invalid))

        if missing:
            msg += MISSING.format(len(missing), list(missing))

        if federation_errors:
            msg += HARVESTING_ERRORS.format(len(federation_errors.keys()), list(federation_errors.keys()))
            msg = append_federation_errors(msg, federation_errors)

        if validation['status'] == 'ERROR':
            # Separado del "if invalid", porque generar ids de distribuciones puede ocultar errores
            msg = append_validation_errors(msg, validation)

        FederationTask.info(task, msg)
        return msg

    except Exception as e:
        msg += TASK_ERROR.format(catalog_id, list(valid), e)
        FederationTask.info(task, msg)
        raise Exception(msg)


def sort_datasets_by_condition(node, catalog):
    catalog_report = catalog.validate_catalog()
    valid_set = {ds['identifier'] for ds in catalog_report['error']['dataset'] if ds['status'] == 'OK'}
    invalid_set = {ds['identifier'] for ds in catalog_report['error']['dataset'] if ds['status'] == 'ERROR'}
    dataset_models = set(Dataset.objects.filter(catalog__identifier=node.catalog_id, indexable=True, present=True,)
                         .values_list("identifier", flat=True))
    valid_datasets = dataset_models.intersection(valid_set)
    invalid_datasets = dataset_models.intersection(invalid_set)
    missing_datasets = dataset_models - (valid_datasets | invalid_datasets)
    return valid_datasets, invalid_datasets, missing_datasets


def get_catalog_from_node(node):
    try:
        catalog = DataJson(node.catalog_url)
        return catalog

    except Exception:
        dictionary = json.loads(node.catalog)
        if dictionary:
            catalog = DataJson(dictionary)
            return catalog
        else:
            return None

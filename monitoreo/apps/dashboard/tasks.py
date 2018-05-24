#! coding: utf-8

import logging
import json
from django_rq import job

from pydatajson.core import DataJson
from pydatajson.federation import harvest_catalog_to_ckan
from django_datajsonar.models import Node, Dataset
from .models import HarvestingNode, FederationTask
from .helpers import FederationTaskHandler


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
        federate_catalog.delay(node, portal_url, apikey, task)


@job('indexing', timeout=1800)
def federate_catalog(node, portal_url, apikey, task):
    set_logger(task)
    catalog = get_catalog_from_node(node)
    catalog_id = node.catalog_id
    total = Dataset.objects.filter(indexable=True, catalog__identifier=catalog_id).count()
    msg = u"Catálogo: %s\n" % node.catalog_id
    if not catalog:
        msg += u"No se puede acceder al catálogo: %s\n" % node.catalog_id
        FederationTask.info(task, msg)
        raise Exception(msg)

    catalog.generate_distribution_ids()
    valid, invalid, missing = get_dataset_lists(node, catalog)

    try:
        harvested_ids = harvest_catalog_to_ckan(catalog, portal_url, apikey, catalog_id, list(valid))
        msg += u"Se federaron %s de %s datasets.\n" \
               u"%s tuvieron errores de validacion:\n"\
               u"%s \n"\
               u"%s ausentes:\n"\
               u"%s \n" % \
               (len(harvested_ids), total, len(invalid), list(invalid), len(missing), list(missing))
        FederationTask.info(task, msg)
        return msg

    except Exception as e:
        msg += u"Error federando catalog: %s datasets: %s - Error: %s\n" % \
               (catalog_id, list(valid), e)
        FederationTask.info(task, msg)
        raise Exception(msg)


def get_dataset_lists(node, catalog):
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


def set_logger(task):
    logger = logging.getLogger('pydatajson')
    logger.setLevel(level=logging.ERROR)
    fh = FederationTaskHandler(task)
    fh_formatter = logging.Formatter('%(asctime)s :%(filename)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

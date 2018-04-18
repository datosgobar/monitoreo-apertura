#! coding: utf-8

from pydatajson.core import DataJson
from pydatajson.federation import harvest_catalog_to_ckan
from django_datajsonar.apps.management.models import Node
from django_datajsonar.apps.api.models import Dataset
from .models import HarvestingNode


def harvest_run():
    harvesting_nodes = HarvestingNode.objects.filter(enabled=True)
    for harvester in harvesting_nodes:
        portal_url = harvester.url
        apikey = harvester.apikey
        harvest_catalog(portal_url, apikey)


def harvest_catalog(portal_url, apikey):
    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        catalog_id = node.catalog_id
        catalog = DataJson(node.catalog_url)
        dataset_list = get_dataset_list(node, catalog)
        try:
            harvest_catalog_to_ckan(catalog, portal_url, apikey, catalog_id, dataset_list)
        except Exception:
            pass


def get_dataset_list(node, catalog):
    datasets = Dataset.objects.filter(catalog__identifier=node.catalog_id, indexable=True)
    catalog_report = catalog.validate_catalog()
    valid_datasets = set([ds['identifier'] for ds in catalog_report['error']['dataset']
                          if ds['status'] == 'OK'])
    return [dataset.identifier for dataset in datasets
            if dataset.identifier in valid_datasets]


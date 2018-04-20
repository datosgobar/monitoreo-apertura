#! coding: utf-8
from ckanapi.errors import ValidationError, NotAuthorized
from pydatajson.core import DataJson
from pydatajson.federation import harvest_catalog_to_ckan
from django_datajsonar.apps.management.models import Node
from django_datajsonar.apps.api.models import Dataset
from .models import HarvestingNode


def federation_run():
    harvesting_nodes = HarvestingNode.objects.filter(enabled=True)
    for harvester in harvesting_nodes:
        portal_url = harvester.url
        apikey = harvester.apikey
        federate_catalog(portal_url, apikey)


def federate_catalog(portal_url, apikey):
    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        catalog_id = node.catalog_id
        catalog = DataJson(node.catalog_url)
        dataset_list = get_dataset_list(node)
        try:
            harvest_catalog_to_ckan(catalog, portal_url, apikey, catalog_id, dataset_list)
        except (NotAuthorized, ValidationError, KeyError):
            pass


def get_dataset_list(node):
    datasets = Dataset.objects.filter(catalog__identifier=node.catalog_id, indexable=True)
    return [dataset.identifier for dataset in datasets]

#! coding: utf-8

from django.conf import settings

from pydatajson.core import DataJson
from pydatajson.federation import harvest_catalog_to_ckan
from django_datajsonar.apps.management.models import Node
from django_datajsonar.apps.api.models import Dataset


def federation_run():
    portal_url = getattr(settings, 'HARVESTING_URL', None)
    apikey = getattr(settings, 'HARVESTING_URL_APIKEY', None)

    nodes = Node.objects.filter(indexable=True)
    for node in nodes:
        catalog_id = node.catalog_id
        catalog = DataJson(node.catalog_url)
        dataset_list = get_dataset_list(node)
        harvest_catalog_to_ckan(catalog, portal_url, apikey, catalog_id, dataset_list)


def get_dataset_list(node):
    datasets = Dataset.objects.filter(catalog__identifier=node.catalog_id, indexable=True)
    return [dataset.identifier for dataset in datasets]

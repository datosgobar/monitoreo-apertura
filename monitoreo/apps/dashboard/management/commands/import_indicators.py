from __future__ import unicode_literals

import argparse

from tablib import Dataset
from import_export.resources import modelresource_factory

from django.core.management.base import BaseCommand

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador


class Command(BaseCommand):
    help = """Toma el path a un csv de la forma (forma) y crea o actualiza los
    indicadores"""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('rw'))
        parser.add_argument('--aggregated', action='store_true')

    def handle(self, *args, **options):
        model = IndicadorRed if options['aggregated'] else Indicador

        with options['file'] as indicators_csv:
            dataset = Dataset().load(indicators_csv.read())
            indicator_resource = modelresource_factory(model=model)()
            result = indicator_resource.import_data(dataset)
            print(result.totals)

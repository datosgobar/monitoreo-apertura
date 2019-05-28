from __future__ import unicode_literals

import argparse

from import_export.resources import modelresource_factory

from django.core.management.base import BaseCommand

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador, \
    IndicadorFederador
from monitoreo.apps.dashboard.admin.indicators import IndicadorRedResource, IndicatorResource

MODEL_CHOICES = {
    'node': (Indicador, IndicatorResource),
    'network': (IndicadorRed, IndicadorRedResource),
    'federator': (IndicadorFederador, IndicatorResource)
}


class Command(BaseCommand):
    help = """Exporta la base de indicadores en un csv. Por default exporta los
    indicadores de nodo. Para exportar los indicadores de red, pasar
    --aggregated."""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('w'))
        parser.add_argument('--type',
                            choices=['node', 'network', 'federator'],
                            default='node')

    def handle(self, *args, **options):
        model = MODEL_CHOICES[options['type']][0]
        model_resource = MODEL_CHOICES[options['type']][1]
        indicator_resource = modelresource_factory(model,
                                                   resource_class=model_resource)()
        result = indicator_resource.export()
        with options['file'] as export_csv:
            export_csv.write(result.csv)

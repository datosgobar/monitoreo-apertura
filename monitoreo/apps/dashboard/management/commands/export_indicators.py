from __future__ import unicode_literals

import argparse
import csv

from django.core.management.base import BaseCommand

from monitoreo.apps.dashboard.custom_generators import fieldnames_to_headers
from monitoreo.apps.dashboard.models import IndicadorRed, Indicador, \
    IndicadorFederador

AGGREGATED_FIELDNAMES = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
NODE_FIELDNAMES = AGGREGATED_FIELDNAMES + ['jurisdiccion_nombre', 'jurisdiccion_id']

MODEL_CHOICES = {
    'node': (Indicador, NODE_FIELDNAMES),
    'network': (IndicadorRed, AGGREGATED_FIELDNAMES),
    'federator': (IndicadorFederador, NODE_FIELDNAMES)
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
        fieldnames = MODEL_CHOICES[options['type']][1]
        headers = fieldnames_to_headers(fieldnames)
        queryset = model.objects.values(*fieldnames)
        rows = list(queryset)
        writer = csv.DictWriter(options['file'], fieldnames=fieldnames)
        writer.writerow(dict(zip(fieldnames, headers)))
        for row in rows:
            writer.writerow(row)

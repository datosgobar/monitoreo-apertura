from __future__ import unicode_literals

import argparse

from django.core.management.base import BaseCommand
from monitoreo.apps.dashboard.management.import_utils import \
    validate_indicators_csv
from monitoreo.apps.dashboard.management.indicators_validator import \
    write_problems
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, \
    IndicadorFederador

MODEL_CHOICES = {
    'node': Indicador,
    'network': IndicadorRed,
    'federator': IndicadorFederador,
}


class Command(BaseCommand):
    help = """Valida el csv pasado por parametro y devuelve un reporte con los
    errores. Si se pasa el argumento -w escribe el reporte en ese path."""

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument('-w', '--write_path', type=argparse.FileType('w'))
        parser.add_argument('--type',
                            choices=['node', 'network', 'federator'],
                            default='node')

    def handle(self, *args, **options):
        model = MODEL_CHOICES[options['type']]
        with options['file'] as indicators_csv:
            error_list = validate_indicators_csv(indicators_csv, model)
        if not error_list:
            self.stdout.write('Archivo válido')
            return
        if options.get('write_path'):
            with options['write_path'] as report_file:
                write_problems(error_list, report_file)
        else:
            write_problems(error_list, self.stdout)

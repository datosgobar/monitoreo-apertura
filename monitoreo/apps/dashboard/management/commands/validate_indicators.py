from __future__ import unicode_literals

import argparse
import json

from django.core.management.base import BaseCommand
from monitoreo.apps.dashboard.management.command_utils import \
    validate_indicators_csv


class Command(BaseCommand):
    help = """Valida el csv pasado por parametro y devuelve un reporte con los
    errores. Si se pasa el argumento -w escribe el reporte en ese path."""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))
        parser.add_argument('-a', '--aggregated', action='store_true')
        parser.add_argument('-w', '--write_path', type=argparse.FileType('w'))

    def handle(self, *args, **options):
        aggregated = options['aggregated']
        with options['file'] as indicators_csv:
            error_list = validate_indicators_csv(indicators_csv, aggregated)
        if not error_list:
            self.stdout.write('Archivo válido')
            return
        if options.get('write_path'):
            with options['write_path'] as report_file:
                json.dump(error_list, report_file, indent=4)
        else:
            self.stdout.write(json.dumps(error_list, indent=4))

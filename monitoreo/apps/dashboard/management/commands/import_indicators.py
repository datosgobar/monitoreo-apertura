from __future__ import unicode_literals

import argparse
import csv
from contextlib import contextmanager

from django.core.management.base import BaseCommand
from django.db import transaction

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador


class Command(BaseCommand):
    help = """Toma el path a un csv de la forma
    [id, fecha, indicador_valor, indicador_tipo] para indicadores de red y
    [id, fecha, jurisdiccion_id, jurisdiccion_nombre, indicador_valor,
    indicador_tipo] para indicadores de nodos. Con esos datos crea o actualiza
    los rows de la base de datos correspondientes."""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))
        parser.add_argument('--aggregated', action='store_true')

    def handle(self, *args, **options):
        model = IndicadorRed if options['aggregated'] else Indicador
        indicators = []
        with options['file'] as indicators_csv:
            csv_reader = csv.DictReader(indicators_csv)
            with suppress_autotime(model, ['fecha']):
                with transaction.atomic():
                    for row in csv_reader:
                        # sacarle el valor al row antes
                        filter_fields = {
                            field: row[field] for field in row if
                            field in ('fecha',
                                      'indicador_tipo',
                                      'jurisdiccion_id')
                        }
                        model.objects.filter(**filter_fields).delete()
                        indicators.append(model(**row))

                    model.objects.bulk_create(indicators)


@contextmanager
def suppress_autotime(model, fields):
    _original_values = {}
    for field in model._meta.local_fields:
        if field.name in fields:
            _original_values[field.name] = {
                'auto_now': field.auto_now,
                'auto_now_add': field.auto_now_add,
            }
            field.auto_now = False
            field.auto_now_add = False
    try:
        yield
    finally:
        for field in model._meta.local_fields:
            if field.name in fields:
                field.auto_now = _original_values[field.name]['auto_now']
                field.auto_now_add = _original_values[field.name]['auto_now_add']

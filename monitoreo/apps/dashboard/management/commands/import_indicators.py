from __future__ import unicode_literals

import argparse

from contextlib import contextmanager
from tablib import Dataset
from import_export.resources import modelresource_factory

from django.core.management.base import BaseCommand

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador


class Command(BaseCommand):
    help = """Toma el path a un csv de la forma
    [id, fecha, indicador_valor, indicador_tipo] para indicadores de red y
    [id, fecha, jurisdiccion_id, jurisdiccion_nombre, indicador_valor,
    indicador_tipo] para indicadores de nodos. Con esos datos crea o actualiza
    los rows de la base de datos correspondientes."""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('rw'))
        parser.add_argument('--aggregated', action='store_true')

    def handle(self, *args, **options):
        model = IndicadorRed if options['aggregated'] else Indicador

        with options['file'] as indicators_csv:
            with suppress_autotime(model, ['fecha']):
                dataset = Dataset().load(indicators_csv.read())
                indicator_resource = modelresource_factory(model=model)()
                result = indicator_resource.import_data(dataset)
                print result.totals


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

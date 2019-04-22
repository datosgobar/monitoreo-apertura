from __future__ import unicode_literals

import argparse
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from monitoreo.apps.dashboard.context_managers import suppress_autotime
from monitoreo.apps.dashboard.models import IndicadorRed, Indicador,\
    IndicatorType
from monitoreo.apps.dashboard.management.indicators_validator import \
    ValidationError
from monitoreo.apps.dashboard.management.command_utils import \
    invalid_indicators_csv


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
        aggregated = options['aggregated']
        model = IndicadorRed if aggregated else Indicador
        indicators = []
        types_ids = IndicatorType.objects.values('nombre', 'id')
        types_mapping = {ind_type['nombre']: ind_type['id'] for
                         ind_type in types_ids}
        with options['file'] as indicators_csv:
            # Validación de datos
            if invalid_indicators_csv(indicators_csv, aggregated):
                msg = 'El csv de indicadores es inválido. '\
                      'Correr el comando validate_indicators_csv para un ' \
                      'reporte detallado'
                raise ValidationError(msg)

            csv_reader = csv.DictReader(indicators_csv)
            with suppress_autotime(model, ['fecha']):
                with transaction.atomic():
                    for row in csv_reader:
                        row['indicador_tipo'] = \
                            types_mapping[row['indicador_tipo__nombre']]
                        filter_fields = {
                            field: row[field] for field in row if
                            field in ('fecha',
                                      'indicador_tipo',
                                      'jurisdiccion_id')
                        }
                        model.objects.filter(**filter_fields).delete()
                        indicators.append(model(**row))
                    model.objects.bulk_create(indicators)

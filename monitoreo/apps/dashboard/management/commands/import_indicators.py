from __future__ import unicode_literals

import argparse
import csv
import csvvalidator

from contextlib import contextmanager
from csvvalidator import CSVValidator, datetime_string, enumeration

from django.core.management.base import BaseCommand
from django.db import transaction

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador, IndicatorType


csvvalidator.basestring = str


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


def invalid_indicators_csv(csv_file, aggregated):
    error_list = validate_indicators_csv(csv_file, aggregated)
    return bool(error_list)


def validate_indicators_csv(csv_file, aggregated):
    csv_reader = csv.reader(csv_file)
    validator_generator = IndicatorValidatorGenerator(aggregated)
    validator = validator_generator.generate()
    error_list = validator.validate(csv_reader)
    return error_list


class IndicatorValidatorGenerator(object):
    def __init__(self, aggregated):
        indicator_names = IndicatorType.objects.all()\
            .values_list('nombre', flat=True)
        self.value_checks = [
            ('fecha', datetime_string('%Y-%m-%d')),
            ('indicador_tipo__nombre', enumeration(list(indicator_names))),
            ('indicador_valor', str),
        ]
        self.unique_checks = ('fecha',
                              'indicador_tipo__nombre', )
        if not aggregated:
            self.value_checks = self.value_checks + [
                ('jurisdiccion_id', str),
                ('jurisdiccion_nombre', str), ]
            self.unique_checks = self.unique_checks + ('jurisdiccion_id', )

        self.field_names = [check[0] for check in self.value_checks]

    def generate(self):
        validator = CSVValidator(self.field_names)
        validator.add_header_check()
        validator.add_record_length_check()
        for value, check in self.value_checks:
            validator.add_value_check(value, check)
        validator.add_unique_check(self.unique_checks)
        return validator


class ValidationError(ValueError):
    pass

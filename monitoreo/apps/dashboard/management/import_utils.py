import csv
import os

from async_messages import message_user
from django.contrib.messages import constants
from django.db import transaction
from django_rq import job

from monitoreo.apps.dashboard.context_managers import suppress_autotime
from monitoreo.apps.dashboard.management.indicators_validator import \
    IndicatorValidatorGenerator
from monitoreo.apps.dashboard.models import IndicatorType


def invalid_indicators_csv(csv_file, model):
    error_list = validate_indicators_csv(csv_file, model)
    return bool(error_list)


def validate_indicators_csv(csv_file, model):
    with open(csv_file) as indicators_csv:
        csv_reader = csv.reader(indicators_csv)
        validator_generator = IndicatorValidatorGenerator(model)
        validator = validator_generator.generate()
        error_list = validator.validate(csv_reader)
    return error_list


@job('imports', timeout=1800)
def import_from_admin(indicators_file, model, user):
    if invalid_indicators_csv(indicators_file, model):
        invalid_msg = 'El csv de indicadores es inválido. Correr el comando ' \
                      'validate_indicators_csv para un reporte detallado'
        message_user(user, invalid_msg, constants.WARNING)
        return
    valid_msg = 'El csv de indicadores es válido, en breve iniciará' \
                ' el proceso de importación'
    message_user(user, valid_msg, constants.SUCCESS)
    import_indicators_tempfile.delay(indicators_file, model, user)


@job('imports', timeout=1800)
def import_indicators_tempfile(indicators_file, model, user):
    try:
        import_indicators(indicators_file, model)
        msg = 'Los indicadores fueron importados con éxito'
        status = constants.SUCCESS
    except Exception:
        msg = 'Ocurrió un problema importando los indicadores'
        status = constants.ERROR
    finally:
        os.remove(indicators_file)
    message_user(user, msg, status)


def import_indicators(indicators_file, model):
    types_mapping = {ind_type.nombre: ind_type for
                     ind_type in IndicatorType.objects.all()}
    with open(indicators_file) as indicators_csv:
        indicators = []
        csv_reader = csv.DictReader(indicators_csv)
        with suppress_autotime(model, ['fecha']):
            with transaction.atomic():
                for row in csv_reader:
                    row['indicador_tipo'] = \
                        types_mapping[row.pop('indicador_tipo')]
                    filter_fields = {
                        field: row[field] for field in row if
                        field in ('fecha',
                                  'indicador_tipo',
                                  'jurisdiccion_id')
                    }
                    indicators.append(model(**row))
                model.objects.all().delete()
                model.objects.bulk_create(indicators)

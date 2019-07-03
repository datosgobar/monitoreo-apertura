import csv
from io import TextIOWrapper

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
    csv_file = TextIOWrapper(csv_file)
    csv_reader = csv.reader(csv_file)
    validator_generator = IndicatorValidatorGenerator(model)
    validator = validator_generator.generate()
    error_list = validator.validate(csv_reader)
    csv_file.seek(0)
    csv_file.detach()
    return error_list


@job('imports', timeout=1800)
def import_indicators(indicators_file, model):
    indicators_file = TextIOWrapper(indicators_file)
    types_mapping = {ind_type.nombre: ind_type for
                     ind_type in IndicatorType.objects.all()}
    indicators = []
    csv_reader = csv.DictReader(indicators_file)
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
                model.objects.filter(**filter_fields).delete()
                indicators.append(model(**row))
            model.objects.bulk_create(indicators)
    indicators_file.detach()

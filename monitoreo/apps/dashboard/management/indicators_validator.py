import csvvalidator

from csvvalidator import CSVValidator, datetime_string, enumeration

from monitoreo.apps.dashboard.models import IndicatorType
from monitoreo.apps.dashboard.models.indicators import AbstractIndicator

csvvalidator.basestring = str


class IndicatorValidatorGenerator:
    def __init__(self, model):
        indicator_names = IndicatorType.objects.all()\
            .values_list('nombre', flat=True)
        self.value_checks = [
            ('fecha', datetime_string('%Y-%m-%d')),
            ('indicador_tipo__nombre', enumeration(list(indicator_names))),
            ('indicador_valor', str),
        ]
        self.unique_checks = ('fecha',
                              'indicador_tipo__nombre', )
        if not isinstance(model, AbstractIndicator):
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

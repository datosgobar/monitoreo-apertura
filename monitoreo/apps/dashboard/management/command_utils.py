import csv

from monitoreo.apps.dashboard.management.indicators_validator import \
    IndicatorValidatorGenerator


def invalid_indicators_csv(csv_file, aggregated):
    error_list = validate_indicators_csv(csv_file, aggregated)
    return bool(error_list)


def validate_indicators_csv(csv_file, aggregated):
    csv_reader = csv.reader(csv_file)
    validator_generator = IndicatorValidatorGenerator(aggregated)
    validator = validator_generator.generate()
    error_list = validator.validate(csv_reader)
    return error_list

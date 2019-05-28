from __future__ import unicode_literals

import argparse

from django.core.management.base import BaseCommand

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador, \
    IndicadorFederador
from monitoreo.apps.dashboard.management.indicators_validator import \
    ValidationError
from monitoreo.apps.dashboard.management.import_utils import \
    invalid_indicators_csv, import_indicators

MODEL_CHOICES = {
    'node': Indicador,
    'network': IndicadorRed,
    'federator': IndicadorFederador,
}


class Command(BaseCommand):
    help = """Toma el path a un csv de la forma
    [id, fecha, indicador_valor, indicador_tipo] para indicadores de red y
    [id, fecha, jurisdiccion_id, jurisdiccion_nombre, indicador_valor,
    indicador_tipo] para indicadores de nodos. Con esos datos crea o actualiza
    los rows de la base de datos correspondientes."""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('rb'))
        parser.add_argument('--type',
                            choices=['node', 'network', 'federator'],
                            default='node')

    def handle(self, *args, **options):
        model = MODEL_CHOICES[options['type']]
        indicators_file = options['file']

        # Validación de datos
        if invalid_indicators_csv(indicators_file, model):
            msg = 'El csv de indicadores es inválido. ' \
                  'Correr el comando validate_indicators_csv para un ' \
                  'reporte detallado'
            raise ValidationError(msg)

        import_indicators(indicators_file, model)

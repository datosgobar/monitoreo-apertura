from __future__ import unicode_literals

import json
import logging

from pydatajson.helpers import fields_to_uppercase

LOGGER = logging.getLogger(__name__)


def normalize_values(model):
    queryset = model.objects.filter(indicador_tipo__nombre__in=[
        'distribuciones_formatos_cant', 'datasets_frecuencia_cant'])

    for indicator in queryset:
        try:
            value = json.loads(indicator.indicador_valor)
            if isinstance(value, dict):
                normalized_value = fields_to_uppercase(value)
                if normalized_value != value:
                    # No quiero hacer un save si los valores no cambian
                    indicator.indicador_valor = json.dumps(normalized_value)
                    indicator.save()
        except json.JSONDecodeError:
            msg = f'error parseando el indicador:{indicator.pk}'
            LOGGER.warning(msg)


def normalize_node_indicator_values(apps, _schema_editor):
    indicador = apps.get_model('dashboard', 'Indicador')
    normalize_values(indicador)


def normalize_network_indicator_values(apps, _schema_editor):
    indicador_red = apps.get_model('dashboard', 'IndicadorRed')
    normalize_values(indicador_red)


def normalize_federator_indicator_values(apps, _schema_editor):
    indicador_federador = apps.get_model('dashboard', 'IndicadorFederador')
    normalize_values(indicador_federador)

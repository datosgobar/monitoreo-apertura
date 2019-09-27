import csv
import json
import logging

from monitoreo.apps.dashboard.echo import Echo

LOGGER = logging.getLogger(__name__)


def fieldnames_to_headers(fieldnames):
    '''
    'Traduce' nombres de fieldnames de cada modelo de Indicadores a nombres de headers
    para uso en el archivo CSV
    '''
    translations = {
        'fecha': 'fecha',
        'indicador_tipo__nombre': 'indicador_tipo',
        'indicador_valor': 'indicador_valor',
        'jurisdiccion_nombre': 'jurisdiccion_nombre',
        'jurisdiccion_id': 'jurisdiccion_id'
    }
    headers = []
    for fieldname in fieldnames:
        headers.append(translations[fieldname])
    return headers


def prepare_rows(indicator):
    indicator_value = json.loads(indicator['indicador_valor'])
    rows = []
    if isinstance(indicator_value, dict):
        for key, value in indicator_value.items():
            row = indicator.copy()
            row['indicador_apertura'] = key
            row['indicador_valor'] = value
            rows.append(row)
    else:
        row = indicator.copy()
        row['indicador_apertura'] = 'completo'
        row['indicador_valor'] = indicator_value
        rows.append(row)
    return rows


def csv_panel_writer(model, values_lookup):
    buffer = Echo()
    headers_map = model.CSV_PANEL_HEADERS
    indicators = model.objects.csv_panel_indicators().values(*values_lookup)
    writer = csv.DictWriter(buffer, fieldnames=(*headers_map,))

    # La primera row se escribe manualmente porque 'writer.writeheader()' devuelve None
    yield writer.writerow(headers_map)
    for indicator in indicators:
        try:
            rows = prepare_rows(indicator)
            yield from map(writer.writerow, rows)
        except json.JSONDecodeError:
            msg = f'error parseando el indicador:{indicator}'
            LOGGER.warning(msg)

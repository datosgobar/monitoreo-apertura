import csv

from monitoreo.apps.dashboard.echo import Echo
from monitoreo.apps.dashboard.models import IndicadorRed


def fieldnames_to_headers(model):
    '''
    'Traduce' nombres de fieldnames de cada modelo de Indicadores a nombres de headers
    para uso en el archivo CSV
    '''
    translation_dictionary = {
        'fecha': 'fecha',
        'indicador_tipo__nombre': 'indicador_tipo',
        'indicador_valor': 'indicador_valor',
        'jurisdiccion_nombre': 'jurisdiccion_nombre',
        'jurisdiccion_id': 'jurisdiccion_id'
    }
    headers = []
    for fieldname in model.get_fieldnames():
        headers.append(translation_dictionary[fieldname])
    return headers


def custom_row_generator(model):
    fieldnames = model.get_fieldnames()
    headers = fieldnames_to_headers(model)
    queryset = model.objects.values(*fieldnames)
    rows = list(queryset)
    pseudo_buffer = Echo()
    writer = csv.DictWriter(pseudo_buffer, fieldnames=fieldnames)

    # La primera row se escribe manualmente porque 'writer.writeheader()' devuelve None
    yield writer.writerow(dict(zip(fieldnames, headers)))

    for row in rows:
        yield writer.writerow(row)

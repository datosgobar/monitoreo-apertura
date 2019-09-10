import csv

from monitoreo.apps.dashboard.echo import Echo


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


def custom_row_generator(model, fieldnames):
    headers = fieldnames_to_headers(fieldnames)
    queryset = model.objects.values(*fieldnames)
    rows = list(queryset)
    pseudo_buffer = Echo()
    writer = csv.DictWriter(pseudo_buffer, fieldnames=fieldnames)

    # La primera row se escribe manualmente porque 'writer.writeheader()' devuelve None
    yield writer.writerow(dict(zip(fieldnames, headers)))

    for row in rows:
        yield writer.writerow(row)

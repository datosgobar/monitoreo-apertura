import csv

from monitoreo.apps.dashboard.echo import Echo
from monitoreo.apps.dashboard.models import IndicadorRed


def custom_row_generator(model):
    fieldnames = model.get_fieldnames()
    headers = model.get_headers()
    queryset = model.objects.values(*fieldnames)
    rows = list(queryset)
    pseudo_buffer = Echo()
    writer = csv.DictWriter(pseudo_buffer, fieldnames=fieldnames)

    # La primera row se escribe manualmente porque 'writer.writeheader()' devuelve None
    yield writer.writerow(dict(zip(fieldnames, headers)))

    for row in rows:
        yield writer.writerow(row)

import csv

from monitoreo.apps.dashboard.echo import Echo
from monitoreo.apps.dashboard.models import IndicadorRed


def custom_row_generator(model):
    fieldnames = model.get_fieldnames()
    queryset = model.objects.values(*fieldnames)
    rows = list(queryset)
    pseudo_buffer = Echo()
    writer = csv.DictWriter(pseudo_buffer, fieldnames=fieldnames)

    # La primera row se arma 'a mano' porque 'writer.writeheader()' devuelve None
    yield writer.writerow(dict(zip(fieldnames, fieldnames)))

    for row in rows:
        yield writer.writerow(row)


def custom_nodos_indicadores_generator():
    pass

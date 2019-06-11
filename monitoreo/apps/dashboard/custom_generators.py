import csv

from monitoreo.apps.dashboard.echo import Echo
from monitoreo.apps.dashboard.models import IndicadorRed


def custom_row_generator():
    queryset = IndicadorRed.objects.values('fecha', 'indicador_tipo__nombre', 'indicador_valor')
    rows = list(queryset)
    pseudo_buffer = Echo()
    fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
    writer = csv.DictWriter(pseudo_buffer, fieldnames=fieldnames)

    # La primera row se arma 'a mano' porque 'writer.writeheader()' devuelve None
    yield writer.writerow({'fecha': 'fecha',
                           'indicador_tipo__nombre': 'indicador_tipo__nombre',
                           'indicador_valor': 'indicador_valor'})

    for row in rows:
        yield writer.writerow(row)

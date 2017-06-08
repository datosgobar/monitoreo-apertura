from datetime import date, timedelta
from django.shortcuts import render
from monitoreo.apps.dashboard.models import Indicador


def red_nodos(request):
    today = date.today()
    indicadores = Indicador.objects.filter(fecha=today)
    if not indicadores:
        yesterday = today - timedelta(days=1)
        indicadores = Indicador.objects.filter(fecha=yesterday)

    if not indicadores:  # Error, no hay indicadores cargados
        return render(request, '500.html')

    # El template espera una lista de los indicadores en orden correcto
    catalogs = {}
    indicators_names = ['datasets_actualizados_pct', 'datasets_meta_ok_pct']
    for indicador in indicadores:
        nombre = indicador.catalogo_nombre

        if nombre not in catalogs:
            catalogs[nombre] = []

        if indicador.indicador_nombre in indicators_names:
            index = indicators_names.index(indicador.indicador_nombre)
            catalogs[nombre].insert(index, indicador.indicador_valor)

    context = {
        'indicator_names': indicators_names,
        'catalogs': catalogs
    }

    return render(request, 'nodos/nodos.html', context)

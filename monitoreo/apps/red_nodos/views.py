# coding=utf-8
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

    # Lista de indicadores a mostrar en la tabla (todo: pasarlo a modelos?)
    indicators_names = ['datasets_actualizados_pct', 'datasets_meta_ok_pct']

    # El template espera una diccionario con listas de los indicadores en orden
    # correcto como valores
    catalogs = {}
    for indicador in indicadores:
        nombre = indicador.catalogo_nombre

        if nombre not in catalogs:
            # Primer indicador con este nombre, lo agrego al diccionario
            catalogs[nombre] = []

        if indicador.indicador_nombre in indicators_names:
            # Lo agrego en la posición correcta, 'index'
            index = indicators_names.index(indicador.indicador_nombre)
            catalogs[nombre].insert(index, indicador.indicador_valor)

    context = {
        'indicator_names': indicators_names,
        'catalogs': catalogs
    }

    return render(request, 'nodos/nodos.html', context)

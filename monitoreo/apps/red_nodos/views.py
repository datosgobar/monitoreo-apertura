# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from monitoreo.apps.dashboard.models import Indicador
from .models import TableColumn


def red_nodos(request):
    today = date.today()
    indicators = Indicador.objects.filter(fecha=today)
    if not indicators:
        yesterday = today - timedelta(days=1)
        indicators = Indicador.objects.filter(fecha=yesterday)

    if not indicators:  # Error, no hay indicadores cargados
        return render(request, '500.html')

    catalogs = {}
    columns = TableColumn.objects.all()
    indicator_names = [column.indicator.nombre for column in columns]

    for indicator in indicators:
        catalog_name = indicator.catalogo_nombre
        indicator_name = indicator.indicador_tipo.nombre

        if catalog_name not in catalogs.keys():
            # Primer indicador con este nombre, lo agrego al diccionario
            catalogs[catalog_name] = []

        if indicator_name in indicator_names:
            # Lo agrego en la posición correcta, 'index'
            index = indicator_names.index(indicator_name)
            catalogs[catalog_name].insert(index, indicator.indicador_valor)

    indicator_full_names = [column.full_name for column in columns]
    context = {
        'indicator_names': indicator_full_names,
        'catalogs': catalogs
    }

    return render(request, 'nodos/nodos.html', context)

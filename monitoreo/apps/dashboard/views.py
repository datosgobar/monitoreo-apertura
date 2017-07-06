# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from .models import Indicador, IndicadorRed, TableColumn
from .helpers import fetch_latest_indicadors


def landing(request):
    indicators = IndicadorRed.objects.all()
    # Obtengo los indicadores más recientes, empaquetados en un diccionario
    indicators = fetch_latest_indicadors(indicators)

    if not indicators:  # Error, no hay indicadores cargados
        return render(request, '500.html', status=500)

    documentados_pct = int(indicators['pad_items_documentados_pct'])
    descargables_pct = int(indicators['pad_items_descarga_pct'])
    items = indicators['pad_compromisos_cant']
    jurisdicciones = indicators['pad_jurisdicciones_cant']

    catalogos_cant = indicators['catalogos_cant']
    datasets_cant = indicators['datasets_cant']
    ok_pct = int(indicators['datasets_meta_ok_pct'])
    actualizados_pct = int(indicators['datasets_actualizados_pct'])

    context = {
        'items': items,
        'jurisdicciones': jurisdicciones,
        'catalogos': catalogos_cant,
        'datasets': datasets_cant,
        'documentados_pct': documentados_pct,
        'descargables_pct': descargables_pct,
        'ok_pct': ok_pct,
        'actualizados_pct': actualizados_pct
    }
    return render(request, 'dashboard/landing.html', context)


def red_nodos(request):
    return populate_table(request, 'RED')


def compromisos(request):
    return populate_table(request, 'PAD')


def populate_table(request, tipo):
    today = date.today()
    indicators = Indicador.objects.all().filter(indicador_tipo__tipo=tipo,
                                                fecha__day=today.day,
                                                fecha__month=today.month,
                                                fecha__year=today.year)

    if not indicators:
        today = today - timedelta(days=1)
        indicators = Indicador.objects.all().filter(indicador_tipo__tipo=tipo,
                                                    fecha__day=today.day,
                                                    fecha__month=today.month,
                                                    fecha__year=today.year)

    if not indicators:  # Error, no hay indicadores cargados
        return render(request, '500.html')

    catalogs = {}
    columns = TableColumn.objects.all().filter(indicator__tipo=tipo)
    indicator_names = [column.indicator.nombre for column in columns]

    for indicator in indicators:
        catalog_name = indicator.jurisdiccion_nombre
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

    return render(request, 'dashboard/detalle.html', context)

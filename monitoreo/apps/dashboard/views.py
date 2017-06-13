# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from .models import Indicador, IndicadorRed, TableColumn


def landing(request):
    # Obtengo indicadores de la red de ayer
    today = date.today()
    indicators = IndicadorRed.objects.all()

    # Si todavía no se calcularon los indicadores de hoy (12 AM - 5 AM) usamos
    # los de ayer
    if not indicators:
        yesterday = today - timedelta(days=1)
        indicators = IndicadorRed.objects.filter(fecha=yesterday)

    if not indicators:  # Error, no hay indicadores cargados
        return render(request, '500.html', status=500)

    # Valores para mocking, a ser calculados posteriormente
    documentados_pct = 60
    descargables_pct = 75
    items = 0
    jurisdicciones = 0

    # Agarro el valor más reciente que devuelve el filter. El QuerySet no
    # debería estar vacío nunca, si el query anterior de todos los objetos es
    # no nulo, se asume que los indicadores están cargados correctamente
    catalogos_cant = indicators.filter(
        indicador_tipo__nombre="catalogos_cant").latest().indicador_valor

    datasets_cant = indicators.filter(
        indicador_tipo__nombre="datasets_cant").latest().indicador_valor

    ok_pct = indicators.filter(
        indicador_tipo__nombre="datasets_meta_ok_pct").latest().indicador_valor

    actualizados_pct = indicators.filter(
        indicador_tipo__nombre="datasets_actualizados_pct").\
        latest().indicador_valor

    context = {
        'fecha': today,
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

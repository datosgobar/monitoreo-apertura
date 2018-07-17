# coding=utf-8
from datetime import date, timedelta
from django.shortcuts import render
from .models import Indicador, IndicadorRed, TableColumn, IndicatorsGenerationTask, IndicatorType
from .helpers import fetch_latest_indicadors


def landing(request):
    indicators = IndicadorRed.objects.all()
    # Obtengo los indicadores más recientes, empaquetados en un diccionario
    indicators = fetch_latest_indicadors(indicators)

    if not indicators:  # Error, no hay indicadores cargados
        return render(request, '500.html', status=500)

    catalogos_cant = indicators['catalogos_cant']
    datasets_cant = indicators['datasets_cant']
    ok_pct = indicators['datasets_meta_ok_pct']
    actualizados_pct = indicators['datasets_actualizados_pct']

    context = {
        'catalogos': catalogos_cant,
        'datasets': datasets_cant,
        'ok_pct': ok_pct,
        'actualizados_pct': actualizados_pct
    }
    return render(request, 'dashboard/landing.html', context)


def red_nodos(request):
    context = populate_table('RED')
    return render(request, 'dashboard/red.html', context)


def test_report(request):
    context = {
        'finish_time': 'FINNISH TIM'
    }
    a_taks = IndicatorsGenerationTask.objects.last()
    date = a_taks.finished.date()
    latest_indicators = IndicadorRed.objects.filter(fecha=date)
    indicator_dict = {indicator.indicador_tipo.nombre: indicator.indicador_valor for indicator in latest_indicators}
    harvested_datasets = indicator_dict.pop('datasets_federados')
    non_harvested_datasets = indicator_dict.pop('datasets_no_federados')
    context.update({
        'latest_indicators': indicator_dict
    })
    return render(request, 'reports/report.html', context)


def populate_table(tabla):
    today = date.today()
    indicators = Indicador.objects.filter(indicador_tipo__tipo=tabla,
                                          fecha__day=today.day,
                                          fecha__month=today.month,
                                          fecha__year=today.year).\
        order_by('-id')

    if not indicators:
        today = today - timedelta(days=1)
        indicators = Indicador.objects.filter(indicador_tipo__tipo=tabla,
                                              fecha__day=today.day,
                                              fecha__month=today.month,
                                              fecha__year=today.year).\
            order_by('-id')

    if not indicators:  # Error, no hay indicadores cargados
        return {}

    catalogs = {}
    # Agarro las columnas de la tabla pasada
    columns = TableColumn.objects.all().filter(indicator__tipo=tabla)

    # Nombres de los indicadores que estamos buscando para esta tabla
    indicator_names = [column.indicator.nombre for column in columns]

    # Trackea que indicadores ya fueron agregados a cada jurisdicción,
    # diccionario con listas como claves
    added_indicators = {}

    for indicator in indicators:
        jurisdiction_name = indicator.jurisdiccion_nombre
        indicator_name = indicator.indicador_tipo.nombre

        if jurisdiction_name not in catalogs.keys():
            # Primer indicador de esa jurisdicción, lo inicializo en catalogs
            # y added_indicators. Instancio la lista con tantos elementos
            # como indicadores a buscar, para asegurarse que haya valores
            catalogs[jurisdiction_name] = ['N/A' for _ in range(len(columns))]
            added_indicators[jurisdiction_name] = []

        if indicator_name in indicator_names:
            # Ya agregamos un indicador con este nombre, paso
            if indicator_name in added_indicators[jurisdiction_name]:
                continue

            # Lo agrego en la posición correcta, 'index', y a la lista de indicadores agregados
            index = indicator_names.index(indicator_name)
            catalogs[jurisdiction_name][index] = indicator.indicador_valor
            added_indicators[jurisdiction_name].append(indicator_name)

    indicator_full_names = [column.full_name for column in columns]
    context = {
        'indicator_names': indicator_full_names,
        'catalogs': catalogs,
    }

    return context

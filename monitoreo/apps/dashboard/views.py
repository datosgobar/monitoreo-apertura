# coding=utf-8
import csv
from datetime import date, timedelta
from django.shortcuts import render
from django.http import StreamingHttpResponse

from .models import Indicador, IndicadorRed, IndicadorFederador, TableColumn
from .helpers import fetch_latest_indicadors, download_time_series
from .custom_generators import custom_row_generator


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


def indicators_csv(_request, node_id=None, indexing=False):
    if node_id is None:
        queryset = IndicadorRed.objects.\
            filter(indicador_tipo__series_red=True)
    elif indexing:
        queryset = IndicadorFederador.objects.\
            filter(indicador_tipo__series_federadores=True,
                   jurisdiccion_id=node_id)
    else:
        queryset = Indicador.objects.\
            filter(indicador_tipo__series_nodos=True,
                   jurisdiccion_id=node_id)

    return download_time_series(queryset, node_id=node_id)


def create_response_from_indicator_model(model, filename):
    response = StreamingHttpResponse(custom_row_generator(model), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename={}.csv'.format(filename)
    return response


def indicadores_red_csv(_request):
    return create_response_from_indicator_model(IndicadorRed, 'indicadores-red')


def nodos_indicadores_csv(_request):
    return create_response_from_indicator_model(Indicador, 'indicadores-nodo')


def nodos_indicadores_federadores_csv(_request):
    return create_response_from_indicator_model(IndicadorFederador, 'indicadores-federadores')

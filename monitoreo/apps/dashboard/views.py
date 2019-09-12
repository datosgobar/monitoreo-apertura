# coding=utf-8
import os
from datetime import date, timedelta

from django.conf import settings
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseBadRequest

from .models import Indicador, IndicadorRed, IndicadorFederador, TableColumn
from .helpers import download_time_series
from .custom_generators import custom_row_generator


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


def create_response_from_indicator_model(model, fieldnames, filename):
    response = StreamingHttpResponse(custom_row_generator(model, fieldnames), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename={}.csv'.format(filename)
    return response


def indicadores_red_nodos_csv(_request):
    fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
    return create_response_from_indicator_model(IndicadorRed, fieldnames, 'indicadores-red')


def indicadores_nodos_csv(_request):
    fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
    return create_response_from_indicator_model(Indicador, fieldnames, 'indicadores-nodo')


def indicadores_nodos_federadores_csv(_request):
    fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
    return create_response_from_indicator_model(IndicadorFederador, fieldnames, 'indicadores-federadores')


def indicadores_red_series(_request):
    path = os.path.join(settings.MEDIA_ROOT, 'indicator_files', 'indicadores-red-series.csv')
    return streaming_series_response('indicadores-red-nodos-series.csv', path)


def indicadores_nodos_series(_request, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'indicator_files', 'nodes', filename)
    return streaming_series_response(filename, path)


def indicadores_federadores_series(_request, filename):
    path = os.path.join(settings.MEDIA_ROOT, 'indicator_files', 'federator-nodes', filename)
    return streaming_series_response(filename, path)


def streaming_series_response(filename, path):
    if not os.path.exists(path):
        return HttpResponseBadRequest("No hay un archivo generado con ese nombre.")
    response = StreamingHttpResponse(open(path), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename={}'.format(
        filename)
    return response

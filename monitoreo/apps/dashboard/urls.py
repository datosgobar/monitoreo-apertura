#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import indicadores_red_nodos_csv, indicadores_nodos_csv,\
    indicadores_nodos_federadores_csv, indicadores_red_series, indicadores_nodos_series, \
    indicadores_federadores_series, panel_federadores_zip, panel_nodos_zip, panel_red_zip

urlpatterns = [
    url(r'^indicadores/indicadores-red-nodos.gz$', panel_red_zip, name="indicadores-red-zip"),
    url(r'^indicadores/indicadores-nodos.gz$', panel_nodos_zip, name="indicadores-nodo-zip"),
    url(r'^indicadores/indicadores-nodos-federadores.gz$', panel_federadores_zip, name="indicadores-federadores-zip"),

    url(r'^indicadores/panel-red.csv$', indicadores_red_nodos_csv, name="indicadores-red-csv"),
    url(r'^indicadores/panel-nodos.csv$', indicadores_nodos_csv, name="indicadores-nodo-csv"),
    url(r'^indicadores/panel-nodos-federadores.csv$',
        indicadores_nodos_federadores_csv, name="indicadores-federadores-csv"),

    url(r'^indicadores/indicadores-red-nodos-series.csv$', indicadores_red_series, name="indicadores-red-series"),
    url(r'^indicadores/nodos/(?P<filename>[\w|-]+.csv)$', indicadores_nodos_series, name="indicadores-nodos-series"),
    url(r'^indicadores/nodos-federadores/(?P<filename>[\w|-]+.csv)$',
        indicadores_federadores_series, name="indicadores-federadores-series"),
]

#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import landing, red_nodos, indicadores_red_csv, \
    nodos_indicadores_csv, nodos_indicadores_federadores_csv

urlpatterns = [
    url(r'^nodos$', red_nodos, name='nodos'),
    url(r'^indicadores-red.csv$', indicadores_red_csv, name="indicadores-red-csv"),
    url(r'^indicadores-nodo.csv$', nodos_indicadores_csv, name="indicadores-nodo-csv"),
    url(r'^indicadores-federadores.csv$', nodos_indicadores_federadores_csv,
        name="indicadores-federadores-csv")
]

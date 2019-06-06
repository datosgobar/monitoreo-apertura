#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import landing, red_nodos, nodos_indicadores_csv

urlpatterns = [
    url(r'^$', landing, name='landing'),
    url(r'^nodos$', red_nodos, name='nodos'),
    url(r'^nodos-red-indicadores.csv$', nodos_indicadores_csv, name="indicators-csv")
]

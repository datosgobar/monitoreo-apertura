#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import landing, red_nodos, indicadores_red_csv

urlpatterns = [
    url(r'^$', landing, name='landing'),
    url(r'^nodos$', red_nodos, name='nodos'),
    url(r'^nodos-red-indicadores.csv$', indicadores_red_csv, name="indicators-csv")
]

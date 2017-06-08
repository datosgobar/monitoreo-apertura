#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.red_nodos.views import red_nodos

urlpatterns = [
    url(r'^nodos$', red_nodos, name='nodos'),
]

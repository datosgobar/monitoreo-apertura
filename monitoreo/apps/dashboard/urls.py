#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import landing, red_nodos

urlpatterns = [
    url(r'^$', landing, name='landing'),
    url(r'^nodos$', red_nodos, name='nodos')
]

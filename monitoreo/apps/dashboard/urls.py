#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import hello

urlpatterns = [
    url(r'', hello),
]

#! coding: utf-8
from django.conf.urls import url

from monitoreo.apps.dashboard.views import landing

urlpatterns = [
    url(r'^$', landing),
]

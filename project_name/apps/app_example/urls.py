#! coding: utf-8

from django.conf.urls import url

from project_name.apps.app_example.views import hello_world

urlpatterns = [
    url(r'hello/(?P<name>[\w\-]+)/', hello_world),
]

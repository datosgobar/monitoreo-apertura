# coding=utf-8
from __future__ import unicode_literals

from django.apps import AppConfig
from des.apps import DjangoDesConfig


class DashboardConfig(AppConfig):
    name = 'dashboard'


class CustomDesConfig(DjangoDesConfig):
    verbose_name = 'Configuración correo'
    verbose_name_plural = verbose_name
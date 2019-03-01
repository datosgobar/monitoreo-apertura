# coding=utf-8
from __future__ import unicode_literals

from des.models import DynamicEmailConfiguration


class ConfiguracionEmail(DynamicEmailConfiguration):
    class Meta:
        proxy = True
        app_label = 'des'
        verbose_name = "Configuración correo electrónico"

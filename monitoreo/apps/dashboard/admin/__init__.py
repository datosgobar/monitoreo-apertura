# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from des.models import DynamicEmailConfiguration
from des.admin import DynamicEmailConfigurationAdmin

from monitoreo.apps.dashboard.models import ConfiguracionEmail

from . import indicator_types, indicators, nodes, tasks

# Proxies
admin.site.unregister(DynamicEmailConfiguration)
admin.site.register(ConfiguracionEmail, DynamicEmailConfigurationAdmin)

# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from des.models import DynamicEmailConfiguration
from des.admin import DynamicEmailConfigurationAdmin

from django_datajsonar.admin.node import DatasetIndexingFileAdmin
from django_datajsonar.admin.tasks import DataJsonAdmin
from django_datajsonar.models import ReadDataJsonTask, DatasetIndexingFile

from monitoreo.apps.dashboard.models import DatasetFederationFile, \
    NodeReadTask, ConfiguracionEmail

from . import indicator_types, indicators, nodes, tasks

# Proxies
admin.site.unregister(DatasetIndexingFile)
admin.site.unregister(ReadDataJsonTask)
admin.site.unregister(DynamicEmailConfiguration)

admin.site.register(DatasetFederationFile, DatasetIndexingFileAdmin)
admin.site.register(NodeReadTask, DataJsonAdmin)
admin.site.register(ConfiguracionEmail, DynamicEmailConfigurationAdmin)

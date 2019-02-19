# coding=utf-8
from __future__ import unicode_literals

from des.models import DynamicEmailConfiguration
from django_datajsonar.models import DatasetIndexingFile, ReadDataJsonTask


class DatasetFederationFile(DatasetIndexingFile):
    class Meta:
        proxy = True
        app_label = 'django_datajsonar'
        verbose_name_plural = "Dataset federation files"


class NodeReadTask(ReadDataJsonTask):
    class Meta:
        proxy = True
        app_label = 'django_datajsonar'
        verbose_name_plural = "Node read tasks"


class ConfiguracionEmail(DynamicEmailConfiguration):
    class Meta:
        proxy = True
        app_label = 'des'
        verbose_name = "Configuración correo electrónico"

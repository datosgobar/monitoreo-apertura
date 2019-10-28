# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from solo.models import SingletonModel
from django_datajsonar.models import AbstractTask, Node

from .nodes import HarvestingNode


class FederationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de federación"
    harvesting_node = models.ForeignKey(HarvestingNode, models.CASCADE, null=True)


class IndicatorsGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de indicadores"


class ReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Reportes de indicadores"


class ValidationReportTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Reportes de validación"


class NewlyReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Reportes de novedades de datasets"

    def close_task(self):
        self.refresh_from_db()
        self.status = self.FINISHED
        self.finished = timezone.now()
        self.save()


class TasksConfig(SingletonModel):
    validation_url_check = models.BooleanField(
        default=True, verbose_name='Activar validación de URLs con errores de descarga en los reportes')
    indicators_url_check = models.BooleanField(
        default=True, verbose_name='Activar generación de indicadores de URLs con errores de descarga')
    federation_url_check = models.BooleanField(
        default=True, verbose_name='Activar validación de URLs con errores de descarga en la federación')
    indicators_timeout = models.IntegerField(default=1800, help_text="En segundos.")
    validation_timeout = models.IntegerField(default=1800, help_text="En segundos.")
    url_check_timeout = models.IntegerField(default=1, help_text="En segundos.")

    def get_validation_config_for_node(self, node: Node) -> bool:
        return self.validation_url_check and node.validate_catalog_urls

    class Meta:
        verbose_name = "Configuracion general"

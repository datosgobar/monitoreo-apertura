# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django_datajsonar.models import AbstractTask, Node
from solo.models import SingletonModel

from .nodes import HarvestingNode


class FederationTask(AbstractTask):
    class Meta:
        verbose_name = "Corrida de federación"
        verbose_name_plural = "Corridas de federación"
    harvesting_node = models.ForeignKey(HarvestingNode, models.CASCADE, null=True)


class IndicatorsGenerationTask(AbstractTask):
    class Meta:
        verbose_name = "Corrida de indicadores"
        verbose_name_plural = "Corridas de indicadores"


class ReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name = "Reporte de indicadores"
        verbose_name_plural = "Reportes de indicadores"


class ValidationReportTask(AbstractTask):
    class Meta:
        verbose_name = "Reporte de validación"
        verbose_name_plural = "Reportes de validación"


class NewlyReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name = "Reporte de novedades de datasets"
        verbose_name_plural = "Reportes de novedades de datasets"

    def close_task(self):
        self.refresh_from_db()
        self.status = self.FINISHED
        self.finished = timezone.now()
        self.save()


class NotPresentReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name = "Reporte de datasets no presentes"
        verbose_name_plural = "Reportes de datasets no presentes"

    def close_task(self):
        self.refresh_from_db()
        self.status = self.FINISHED
        self.finished = timezone.now()
        self.save()


class TasksConfig(SingletonModel):
    class Meta:
        verbose_name = "Configuración general"
        verbose_name_plural = "Configuraciones generales"

    validation_url_check = models.BooleanField(
        default=False, verbose_name='Activar validación de URLs con errores de descarga en los reportes')
    indicators_url_check = models.BooleanField(
        default=False, verbose_name='Activar generación de indicadores de URLs con errores de descarga')
    federation_url_check = models.BooleanField(
        default=False, verbose_name='Activar validación de URLs con errores de descarga en la federación')
    indicators_timeout = models.IntegerField(default=1800, help_text="En segundos.")
    validation_timeout = models.IntegerField(default=1800, help_text="En segundos.")
    url_check_timeout = models.IntegerField(default=1, help_text="En segundos.")
    url_check_threads = models.IntegerField(
        default=1, verbose_name="Cantidad de threads a usar en el chequeo de links")

    def get_validation_config_for_node(self, node: Node) -> bool:
        return self.validation_url_check and node.validate_catalog_urls

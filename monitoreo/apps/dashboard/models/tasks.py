# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django_datajsonar.models import AbstractTask
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


class DailyReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Reportes de catálogos"

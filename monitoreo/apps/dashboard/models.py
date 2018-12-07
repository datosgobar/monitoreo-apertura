# coding=utf-8
from __future__ import unicode_literals

import json

from collections import OrderedDict

from django.db import models
from django.conf import settings
from ordered_model.models import OrderedModel
from django_datajsonar.models import AbstractTask


class IndicatorQuerySet(models.QuerySet):

    def sorted_indicators_on_date(self, date, node=None):
        indicators = self.filter(fecha=date)
        if node:
            indicators = indicators.filter(jurisdiccion_id=node.catalog_id)
        indicators = indicators.order_by('indicador_tipo__order')

        one_dimensional = OrderedDict()
        multi_dimensional = OrderedDict()
        listed = OrderedDict()
        for indicator in indicators:
            value = json.loads(indicator.indicador_valor)
            if isinstance(value, dict):
                value = OrderedDict(sorted(value.items(), key=lambda t: t[1],
                                           reverse=True))
                multi_dimensional[indicator.indicador_tipo.nombre] = value
            elif isinstance(value, list):
                listed[indicator.indicador_tipo.nombre] = value
            else:
                one_dimensional[indicator.indicador_tipo.nombre] = value

        return one_dimensional, multi_dimensional, listed

    def numerical_indicators_by_date(self, node_id=None):
        indicators = self.order_by('fecha')
        if node_id:
            indicators = indicators.filter(jurisdiccion_id=node_id)

        numerical = OrderedDict()
        for indicator in indicators:
            value = json.loads(indicator.indicador_valor)
            if isinstance(value, (float, int)):
                numerical.setdefault(indicator.fecha, {})\
                    .update({indicator.indicador_tipo.nombre: value})

        return numerical


class IndicatorType(OrderedModel):

    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=100)
    resumen = models.BooleanField(default=False)
    mostrar = models.BooleanField(default=True)
    series_red = models.BooleanField(default=True)
    series_nodos = models.BooleanField(default=True)

    class Meta(OrderedModel.Meta):
        verbose_name_plural = "Tipos de indicadores"

    def __unicode__(self):
        return self.nombre

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class AbstractIndicator(models.Model):
    class Meta:
        abstract = True

    fecha = models.DateField(auto_now_add=True)
    jurisdiccion_nombre = models.CharField(max_length=300)
    jurisdiccion_id = models.CharField(max_length=100, null=True)
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.TextField()

    objects = IndicatorQuerySet.as_manager()


class Indicador(AbstractIndicator):
    class Meta:
        # Nombre en plural para el admin panel de Django
        verbose_name_plural = "Indicadores"

    def __unicode__(self):
        string = 'Indicador "{0}" de {1}, {2}'
        return string.format(self.indicador_tipo.nombre,
                             self.jurisdiccion_nombre,
                             self.fecha)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class IndicadorFederador(AbstractIndicator):
    class Meta:
        # Nombre en plural para el admin panel de Django
        verbose_name_plural = "Indicadores nodos federadores"

    def __unicode__(self):
        string = 'Indicador "{0}" de {1}, {2}'
        return string.format(self.indicador_tipo.nombre,
                             self.jurisdiccion_nombre,
                             self.fecha)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class IndicadorRed(models.Model):
    class Meta:
        # Nombre en plural para el admin panel de Django
        verbose_name_plural = "Indicadores agregados"
        get_latest_by = 'fecha'

    fecha = models.DateField(auto_now_add=True)
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.TextField()

    objects = IndicatorQuerySet.as_manager()

    def __unicode__(self):
        string = 'Indicador "{0}" de la Red de Nodos, {1}'
        return string.format(self.indicador_tipo.nombre, self.fecha)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class TableColumn(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name_plural = "Columnas de la tabla de indicadores de red"

    indicator = models.OneToOneField(IndicatorType, models.CASCADE)
    full_name = models.CharField(max_length=100,
                                 help_text="Usa un valor por defecto si no se especifica",
                                 blank=True)

    def __unicode__(self):
        return 'Columna {}'.format(self.full_name)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def clean(self):
        if not self.full_name:
            for indicator_info in settings.INDICATORS_INFO:
                name = indicator_info['indicador_nombre']
                table_name = indicator_info['indicador_nombre_tabla']
                if self.indicator.nombre == name:
                    self.full_name = table_name
                    break


class HarvestingNode(models.Model):
    class Meta:
        verbose_name_plural = "Nodos federadores"

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.__unicode__()

    name = models.CharField(max_length=100)
    url = models.URLField(help_text='URL del nodo federador ej: http://datos.gob.ar')
    apikey = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)


class FederationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de Federación"
    harvesting_node = models.ForeignKey(HarvestingNode, models.CASCADE, null=True)


class IndicatorsGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de Indicadores"


class ReportGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Envío de Reportes"


class ValidationReportTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Reportes de Validación"

# coding=utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from django.db import models

from .indicator_types import IndicatorType
from .querysets import IndicatorQuerySet


class AbstractIndicator(models.Model):
    class Meta:
        abstract = True

    CSV_PANEL_HEADERS = OrderedDict({
        'fecha': 'fecha',
        'indicador_tipo__nombre': 'indicador_nombre',
        'indicador_apertura': 'indicador_apertura',
        'indicador_valor': 'indicador_valor',
        'jurisdiccion_nombre': 'nodo_nombre',
        'jurisdiccion_id': 'nodo_id'
    })

    fecha = models.DateField(auto_now_add=True)
    jurisdiccion_nombre = models.CharField(max_length=300)
    jurisdiccion_id = models.CharField(max_length=100, null=True)
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.TextField()

    objects = IndicatorQuerySet.as_manager()


class Indicador(AbstractIndicator):

    CSV_PANEL_FIELD = 'panel_nodos'
    CSV_SERIES_FIELD = 'series_nodos'

    class Meta:
        verbose_name = "Indicador de nodos"
        verbose_name_plural = "Tabla de indicadores de nodos"

    def __unicode__(self):
        string = 'Indicador "{0}" de {1}, {2}'
        return string.format(self.indicador_tipo.nombre,
                             self.jurisdiccion_nombre,
                             self.fecha)

    def __str__(self):
        return self.__unicode__()


class IndicadorFederador(AbstractIndicator):

    CSV_PANEL_FIELD = 'panel_federadores'
    CSV_SERIES_FIELD = 'series_federadores'

    class Meta:
        verbose_name = "Indicador de nodos federadores"
        verbose_name_plural = "Tabla de indicadores de nodos federadores"

    def __unicode__(self):
        string = 'Indicador "{0}" de {1}, {2}'
        return string.format(self.indicador_tipo.nombre,
                             self.jurisdiccion_nombre,
                             self.fecha)

    def __str__(self):
        return self.__unicode__()


class IndicadorRed(models.Model):

    CSV_PANEL_HEADERS = OrderedDict({
        'fecha': 'fecha',
        'indicador_tipo__nombre': 'indicador_nombre',
        'indicador_apertura': 'indicador_apertura',
        'indicador_valor': 'indicador_valor',
    })

    CSV_PANEL_FIELD = 'panel_red'
    CSV_SERIES_FIELD = 'series_red'

    class Meta:
        verbose_name = "Indicador de red"
        verbose_name_plural = "Tabla de indicadores de red"
        get_latest_by = 'fecha'

    fecha = models.DateField(auto_now_add=True)
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.TextField()

    objects = IndicatorQuerySet.as_manager()

    def __unicode__(self):
        string = 'Indicador "{0}" de la Red de Nodos, {1}'
        return string.format(self.indicador_tipo.nombre, self.fecha)

    def __str__(self):
        return self.__unicode__()

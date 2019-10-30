# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from ordered_model.models import OrderedModel


class IndicatorType(OrderedModel):
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=100)
    resumen = models.BooleanField(default=False)
    mostrar = models.BooleanField(default=True)
    series_red = models.BooleanField(default=True)
    series_nodos = models.BooleanField(default=True)
    series_federadores = models.BooleanField(default=True)
    panel_red = models.BooleanField(default=True)
    panel_nodos = models.BooleanField(default=True)
    panel_federadores = models.BooleanField(default=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "Tipo de indicador"
        verbose_name_plural = "Tipos de indicadores"

    def __unicode__(self):
        return self.nombre

    def __str__(self):
        return self.__unicode__()


class TableColumn(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name = "Columna de la tabla de indicadores de red"
        verbose_name_plural = "Columnas de la tabla de indicadores de red"

    indicator = models.OneToOneField(IndicatorType, models.CASCADE)
    full_name = models.CharField(max_length=100,
                                 help_text="Usa un valor por defecto si no se especifica",
                                 blank=True)

    def __unicode__(self):
        return 'Columna {}'.format(self.full_name)

    def __str__(self):
        return self.__unicode__()

    def clean(self):
        if not self.full_name:
            for indicator_info in settings.INDICATORS_INFO:
                name = indicator_info['indicador_nombre']
                table_name = indicator_info['indicador_nombre_tabla']
                if self.indicator.nombre == name:
                    self.full_name = table_name
                    break

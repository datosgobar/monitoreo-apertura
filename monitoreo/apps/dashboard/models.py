# coding=utf-8
from __future__ import unicode_literals
from django.utils import timezone
from django.db import models
from ordered_model.models import OrderedModel


class IndicatorType(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=100)

    def __unicode__(self):
        return self.nombre

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class Indicador(models.Model):
    class Meta:
        # Nombre en plural para el admin panel de Django
        verbose_name_plural = "Indicadores"

    fecha = models.DateField()
    jurisdiccion_nombre = models.CharField(max_length=300)
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.CharField(max_length=2000)

    def __init__(self, *args, **kwargs):
        # Columna fecha siempre tiene el timestamp del momento de creación
        kwargs['fecha'] = timezone.now()
        super(Indicador, self).__init__(*args, **kwargs)

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

    fecha = models.DateField()
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.CharField(max_length=300)

    def __init__(self, *args, **kwargs):
        kwargs['fecha'] = timezone.now()
        super(IndicadorRed, self).__init__(*args, **kwargs)

    def __unicode__(self):
        string = 'Indicador "{0}" de la Red de Nodos, {1}'
        return string.format(self.indicador_tipo.nombre, self.fecha)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class TableColumn(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name_plural = "Columnas de la tabla de indicadores de red"

    indicator = models.OneToOneField(IndicatorType, models.CASCADE)
    full_name = models.CharField(max_length=100)

    def __unicode__(self):
        return 'Columna {}'.format(self.full_name)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

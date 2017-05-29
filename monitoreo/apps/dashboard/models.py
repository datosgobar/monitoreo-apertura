# coding=utf-8
from __future__ import unicode_literals
from django.utils import timezone
from django.db import models


class Indicador(models.Model):
    class Meta:
        # Nombre en plural para el admin panel de Django
        verbose_name_plural = "Indicadores"

    fecha = models.DateTimeField()
    catalogo_nombre = models.CharField(max_length=300)
    indicador_nombre = models.CharField(max_length=100)
    indicador_valor = models.CharField(max_length=300)

    def __init__(self, *args, **kwargs):
        # Columna fecha siempre tiene el timestamp del momento de creación
        kwargs['fecha'] = timezone.now()
        super(Indicador, self).__init__(*args, **kwargs)

    def __unicode__(self):
        string = 'Indicador "{0}" del catalogo {1}, {2}'
        return string.format(self.indicador_nombre,
                             self.catalogo_nombre,
                             self.fecha)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class IndicadorRed(Indicador):
    class Meta:
        # Nombre en plural para el admin panel de Django
        verbose_name_plural = "Indicadores de red"

    def __init__(self, *args, **kwargs):
        kwargs['catalogo_nombre'] = "Red de datos"
        super(IndicadorRed, self).__init__(*args, **kwargs)

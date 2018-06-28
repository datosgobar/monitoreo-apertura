# coding=utf-8
from __future__ import unicode_literals
from django.utils import timezone
from django.db import models
from django.conf import settings
from ordered_model.models import OrderedModel
from django_datajsonar.models import AbstractTask


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

    fecha = models.DateField(auto_now_add=True)
    jurisdiccion_nombre = models.CharField(max_length=300)
    indicador_tipo = models.ForeignKey(IndicatorType, models.CASCADE)
    indicador_valor = models.TextField()

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
    url = models.URLField()
    apikey = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)


class FederationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de Federación"
    harvesting_node = models.ForeignKey(HarvestingNode, models.CASCADE, null=True)


class IndicatorsGenerationTask(AbstractTask):
    class Meta:
        verbose_name_plural = "Corridas de Indicadores"

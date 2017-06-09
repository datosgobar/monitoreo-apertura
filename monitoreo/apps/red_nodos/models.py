from __future__ import unicode_literals

from django.db import models
from monitoreo.apps.dashboard.models import IndicatorType


class TableColumn(models.Model):
    class Meta:
        verbose_name_plural = "Columnas de la tabla de indicadores de red"

    indicator = models.ForeignKey(IndicatorType, models.CASCADE)
    full_name = models.CharField(max_length=100)

    def __unicode__(self):
        return 'Columna {}'.format(self.full_name)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

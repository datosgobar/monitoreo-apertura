from __future__ import unicode_literals

from django.db import models


class TableColumn(models.Model):
    class Meta:
        verbose_name_plural = "Columnas de la tabla de indicadores de red"

    indicator = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return 'Columna {}'.format(self.full_name)

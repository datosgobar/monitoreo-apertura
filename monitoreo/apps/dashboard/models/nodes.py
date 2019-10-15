# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from solo.models import SingletonModel


class HarvestingNode(models.Model):
    class Meta:
        verbose_name_plural = "Nodos federadores"

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()

    catalog_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    url = models.URLField(help_text='URL del nodo federador ej: http://datos.gob.ar')
    apikey = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)
    timezone = models.CharField(max_length=100, default="America/Buenos_Aires")


class CentralNode(SingletonModel):
    class Meta:
        verbose_name = "Nodo central"
    node = models.OneToOneField(HarvestingNode, on_delete=models.CASCADE,
                                null=True, blank=True)

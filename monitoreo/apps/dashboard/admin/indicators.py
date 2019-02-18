# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.conf.urls import url

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from monitoreo.apps.dashboard.views import indicators_csv
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed,\
    IndicadorFederador


class IndicatorResource(resources.ModelResource):
    class Meta:
        model = Indicador
        fields = export_order = (
            'id',
            'fecha',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
            'indicador_valor',
            'indicador_tipo'
        )


@admin.register(Indicador)
class IndicatorAdmin(ImportExportModelAdmin):
    list_filter = ('jurisdiccion_id',)
    resource_class = IndicatorResource

    def get_urls(self):
        urls = super(IndicatorAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<node_id>.+)/series-indicadores/$',
                          indicators_csv, name='node_series'), ]
        return extra_urls + urls


class IndexingIndicatorResource(resources.ModelResource):
    class Meta:
        model = IndicadorFederador
        fields = export_order = (
            'id',
            'fecha',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
            'indicador_valor',
            'indicador_tipo'
        )


@admin.register(IndicadorFederador)
class IndexingIndicatorAdmin(ImportExportModelAdmin):
    list_filter = ('jurisdiccion_id',)
    resource_class = IndexingIndicatorResource

    def get_urls(self):
        urls = super(IndexingIndicatorAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<node_id>.+)/series-indicadores/$',
                          indicators_csv, name='indexing_series',
                          kwargs={'indexing': True}), ]
        return extra_urls + urls


class IndicadorRedResource(resources.ModelResource):
    class Meta:
        model = IndicadorRed
        fields = export_order = (
            'id',
            'fecha',
            'indicador_valor',
            'indicador_tipo'
        )


@admin.register(IndicadorRed)
class IndicatorRedAdmin(ImportExportModelAdmin):
    resource_class = IndicadorRedResource

    def get_urls(self):
        urls = super(IndicatorRedAdmin, self).get_urls()
        extra_urls = [url(r'^series-indicadores/$', indicators_csv,
                          name='network_series'), ]
        return extra_urls + urls

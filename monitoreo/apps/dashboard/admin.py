# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.conf.urls import url
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from ordered_model.admin import OrderedModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django_datajsonar.admin import AbstractTaskAdmin

from . import models
from .tasks import federate_catalogs
from .indicators_tasks import generate_indicators
from .report_tasks import send_reports, send_validations
from .views import indicators_csv


def switch(updates):
    return lambda _, __, queryset: queryset.update(**updates)


class TableColumnAdmin(OrderedModelAdmin):
    list_display = ('full_name', 'move_up_down_links')


class IndicatorResource(resources.ModelResource):

    class Meta:
        model = models.Indicador
        fields = export_order = (
            'id',
            'fecha',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
            'indicador_valor',
            'indicador_id'
        )


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
        model = models.IndicadorFederador
        fields = export_order = (
            'id',
            'fecha',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
            'indicador_valor',
            'indicador_id'
        )


class IndexingIndicatorAdmin(ImportExportModelAdmin):
    list_filter = ('jurisdiccion_id',)

    resource_class = IndexingIndicatorResource

    def get_urls(self):
        urls = super(IndexingIndicatorAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<node_id>.+)/series-indicadores/$',
                          indicators_csv, name='node_series',
                          kwargs={'indexing': True}), ]
        return extra_urls + urls


class IndicadorRedResource(resources.ModelResource):
    class Meta:
        model = models.IndicadorRed
        fields = export_order = (
            'id',
            'fecha',
            'indicador_valor',
            'indicador_tipo'
        )


class IndicatorRedAdmin(ImportExportModelAdmin):
    resource_class = IndicadorRedResource

    def get_urls(self):
        urls = super(IndicatorRedAdmin, self).get_urls()
        extra_urls = [url(r'^series-indicadores/$', indicators_csv,
                          name='network_series'), ]
        return extra_urls + urls


class IndicatorTypeAdmin(OrderedModelAdmin):
    list_display = ('nombre', 'order', 'resumen', 'mostrar',
                    'series_red', 'series_nodos',
                    'move_up_down_links', 'position_actions')
    list_filter = ('resumen', 'mostrar')
    actions = ('queryset_to_top', 'queryset_to_bottom',
               'summarize', 'desummarize',
               'show', 'hide',
               'add_to_aggregated_series', 'remove_from_aggregated_series',
               'add_to_nodes_series', 'remove_from_nodes_series',
               'add_to_indexing_series', 'remove_from_indexing_series')

    def get_urls(self):
        urls = super(IndicatorTypeAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<model_id>.+)/(?P<direction>top|bottom)/$',
                          self.order_move, name='order_move'), ]
        return extra_urls + urls

    def position_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Tope</a>&nbsp;'
            '<a class="button" href="{}">Fondo</a>',
            reverse('admin:order_move', args=[obj.pk, 'top']),
            reverse('admin:order_move', args=[obj.pk, 'bottom']),
        )
    position_actions.short_description = 'Posicionamientos'
    position_actions.allow_tags = True

    def order_move(self, request, model_id, direction):
        indicator_type = models.IndicatorType.objects.get(pk=model_id)
        if direction == 'top':
            indicator_type.top()
        elif direction == 'bottom':
            indicator_type.bottom()
        indicator_type.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    summarize = switch({'resumen': True})
    summarize.short_description = 'Agregar al resumen'

    desummarize = switch({'resumen': False})
    desummarize.short_description = 'Quitar del resumen'

    show = switch({'mostrar': True})
    show.short_description = 'Agregar al reporte'

    hide = switch({'mostrar': False})
    hide.short_description = 'Quitar del reporte'

    add_to_aggregated_series = switch({'series_red': True})
    add_to_aggregated_series.short_description =\
        'Agregar a las series de tiempo de red'

    remove_from_aggregated_series = switch({'series_red': False})
    remove_from_aggregated_series.short_description =\
        'Quitar de las series de tiempo de red'

    add_to_nodes_series = switch({'series_nodos': True})
    add_to_nodes_series.short_description = \
        'Agregar a las series de tiempo de nodos'

    remove_from_nodes_series = switch({'series_nodos': False})
    remove_from_nodes_series.short_description = \
        'Quitar de las series de tiempo de nodos'

    add_to_indexing_series = switch({'series_indexadores': True})
    add_to_indexing_series.short_description = \
        'Agregar a las series de tiempo de nodos indexadores'

    remove_from_indexing_series = switch({'series_indexadores': False})
    remove_from_indexing_series.short_description = \
        'Quitar de las series de tiempo de nodos indexadores'


class HarvestingNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'enabled')
    actions = ('federate', 'enable', 'disable')

    enable = switch({'enabled': True})
    enable.short_description = 'Habilitar como nodo federador'

    disable = switch({'enabled': False})
    disable.short_description = 'Inhabilitar federacion del nodo'

    def federate(self, _, queryset):
        for harvesting_node in queryset:
            task = models.FederationTask.objects.create(
                harvesting_node=harvesting_node)
            federate_catalogs.delay(task)
    federate.short_description = 'Correr federacion'


class FederationAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs',)
    exclude = ('status', 'finished',)
    list_display = ('__unicode__',)

    model = models.FederationTask
    task = federate_catalogs
    callable_str = 'monitoreo.apps.dashboard.tasks.federation_run'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('harvesting_node',)
        else:
            return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "harvesting_node":
            kwargs["queryset"] = \
                models.HarvestingNode.objects.filter(enabled=True)
        return super(FederationAdmin, self)\
            .formfield_for_foreignkey(db_field, request, **kwargs)


class IndicatorTaskAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = models.IndicatorsGenerationTask
    task = generate_indicators
    callable_str = 'monitoreo.apps.dashboard.indicators_tasks.indicators_run'


class ReportAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = models.ReportGenerationTask
    task = send_reports
    callable_str = 'monitoreo.apps.dashboard.report_tasks.send_reports'


class ValidationReportAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = models.ValidationReportTask
    task = send_validations
    callable_str = 'monitoreo.apps.dashboard.report_tasks.send_validations'


admin.site.register(models.ValidationReportTask, ValidationReportAdmin)
admin.site.register(models.ReportGenerationTask, ReportAdmin)
admin.site.register(models.FederationTask, FederationAdmin)
admin.site.register(models.IndicatorsGenerationTask, IndicatorTaskAdmin)
admin.site.register(models.HarvestingNode, HarvestingNodeAdmin)
admin.site.register(models.Indicador, IndicatorAdmin)
admin.site.register(models.IndicadorFederador, IndexingIndicatorAdmin)
admin.site.register(models.IndicadorRed, IndicatorRedAdmin)
admin.site.register(models.IndicatorType, IndicatorTypeAdmin)
admin.site.register(models.TableColumn, TableColumnAdmin)

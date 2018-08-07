# coding=utf-8

from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django_datajsonar.admin import AbstractTaskAdmin

from .models import IndicadorRed, Indicador, IndicatorType, TableColumn, HarvestingNode,\
    FederationTask, IndicatorsGenerationTask, ReportGenerationTask
from .tasks import federate_catalogs
from .indicators_tasks import generate_indicators
from .report_tasks import send_reports


def switch(field, boolean):
    return lambda _, __, queryset: queryset.update(**{field: boolean})


class TableColumnAdmin(OrderedModelAdmin):
    list_display = ('full_name', 'move_up_down_links')


class IndicatorResource(resources.ModelResource):

    class Meta:
        model = Indicador
        fields = export_order = (
            'fecha',
            'jurisdiccion_nombre',
            'indicador_tipo__nombre',
            'indicador_valor'
        )


class IndicatorAdmin(ImportExportModelAdmin):
    list_filter = ('jurisdiccion_id',)

    resource_class = IndicatorResource


class IndicadorRedResource(resources.ModelResource):
    class Meta:
        model = IndicadorRed
        fields = export_order = (
            'fecha',
            'indicador_tipo__nombre',
            'indicador_valor'
        )


class IndicatorRedAdmin(ImportExportModelAdmin):
    resource_class = IndicadorRedResource


class IndicatorTypeAdmin(OrderedModelAdmin):
    list_display = ('nombre', 'order', 'resumen', 'mostrar', 'move_up_down_links')
    list_filter = ('resumen', 'mostrar')
    actions = ('queryset_to_top', 'queryset_to_bottom', 'summarize', 'desummarize', 'show', 'hide')

    summarize = switch('resumen', True)
    summarize.short_description = 'Agregar al resumen'

    desummarize = switch('resumen', False)
    desummarize.short_description = 'Quitar del resumen'

    show = switch('mostrar', True)
    show.short_description = 'Agregar al reporte'

    hide = switch('mostrar', False)
    hide.short_description = 'Quitar del reporte'


class HarvestingNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'enabled')
    actions = ('federate', 'enable', 'disable')

    enable = switch('enabled', True)
    enable.short_description = 'Habilitar como nodo federador'

    disable = switch('enabled', False)
    disable.short_description = 'Inhabilitar federacion del nodo'

    def federate(self, _, queryset):
        for harvesting_node in queryset:
            task = FederationTask.objects.create(harvesting_node=harvesting_node)
            portal_url = harvesting_node.url
            apikey = harvesting_node.apikey
            federate_catalogs.delay(portal_url, apikey, task.pk)
    federate.short_description = 'Correr federacion'


class FederationAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'logs',)
    exclude = ('status', 'finished',)
    list_display = ('__unicode__',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('harvesting_node',)
        else:
            return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "harvesting_node":
            kwargs["queryset"] = HarvestingNode.objects.filter(enabled=True)
        return super(FederationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super(FederationAdmin, self).save_model(request, obj, form, change)
        federate_catalogs.delay(obj.harvesting_node.url,
                                obj.harvesting_node.apikey,
                                obj.pk)


class IndicatorTaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    def save_model(self, request, obj, form, change):
        super(IndicatorTaskAdmin, self).save_model(request, obj, form, change)
        generate_indicators.delay(obj.pk)


class ReportAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = ReportGenerationTask
    task = send_reports


admin.site.register(ReportGenerationTask, ReportAdmin)
admin.site.register(FederationTask, FederationAdmin)
admin.site.register(IndicatorsGenerationTask, IndicatorTaskAdmin)
admin.site.register(HarvestingNode, HarvestingNodeAdmin)
admin.site.register(Indicador, IndicatorAdmin)
admin.site.register(IndicadorRed, IndicatorRedAdmin)
admin.site.register(IndicatorType, IndicatorTypeAdmin)
admin.site.register(TableColumn, TableColumnAdmin)

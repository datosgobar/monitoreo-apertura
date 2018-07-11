# coding=utf-8

from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import IndicadorRed, Indicador, TableColumn, HarvestingNode, FederationTask, IndicatorsGenerationTask
from .tasks import federate_catalogs
from .indicators_tasks import generate_indicators


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


class HarvestingNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'enabled')
    actions = ('federate', 'enable', 'disable')

    def enable(self, _, queryset):
        queryset.update(enabled=True)
    enable.short_description = 'Habilitar como nodo federador'

    def disable(self, _, queryset):
        queryset.update(enabled=False)
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


admin.site.register(FederationTask, FederationAdmin)
admin.site.register(IndicatorsGenerationTask, IndicatorTaskAdmin)
admin.site.register(HarvestingNode, HarvestingNodeAdmin)
admin.site.register(Indicador, IndicatorAdmin)
admin.site.register(IndicadorRed, IndicatorRedAdmin)
admin.site.register(TableColumn, TableColumnAdmin)

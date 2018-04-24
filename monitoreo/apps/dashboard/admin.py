from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import IndicadorRed, Indicador, TableColumn, HarvestingNode
from .tasks import federate_catalog


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
            portal_url = harvesting_node.url
            apikey = harvesting_node.apikey
            federate_catalog.delay(portal_url, apikey)
    federate.short_description = 'Correr federacion'


admin.site.register(HarvestingNode, HarvestingNodeAdmin)
admin.site.register(Indicador, IndicatorAdmin)
admin.site.register(IndicadorRed, IndicatorRedAdmin)
admin.site.register(TableColumn, TableColumnAdmin)

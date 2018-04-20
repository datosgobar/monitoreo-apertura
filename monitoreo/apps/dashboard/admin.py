from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import IndicadorRed, Indicador, TableColumn


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


admin.site.register(Indicador, IndicatorAdmin)
admin.site.register(IndicadorRed, IndicatorRedAdmin)
admin.site.register(TableColumn, TableColumnAdmin)

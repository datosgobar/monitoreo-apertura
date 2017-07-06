from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import IndicadorRed, Indicador, TableColumn

admin.site.register(Indicador)
admin.site.register(IndicadorRed)


class TableColumnAdmin(OrderedModelAdmin):
    list_display = ('full_name', 'move_up_down_links')

admin.site.register(TableColumn, TableColumnAdmin)

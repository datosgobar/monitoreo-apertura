from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import IndicadorRed, Indicador, TableColumn, IndicadorPAD

admin.site.register(Indicador)
admin.site.register(IndicadorRed)
admin.site.register(IndicadorPAD)

class TableColumnAdmin(OrderedModelAdmin):
    list_display = ('full_name', 'move_up_down_links')

admin.site.register(TableColumn, TableColumnAdmin)

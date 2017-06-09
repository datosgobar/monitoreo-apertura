from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import TableColumn


class TableColumnAdmin(OrderedModelAdmin):
    list_display = ('full_name', 'move_up_down_links')

admin.site.register(TableColumn, TableColumnAdmin)


# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.conf.urls import url
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from ordered_model.admin import OrderedModelAdmin
from monitoreo.apps.dashboard.models import IndicatorType, TableColumn

from monitoreo.apps.dashboard.admin.utils import switch


@admin.register(TableColumn)
class TableColumnAdmin(OrderedModelAdmin):
    list_display = ('full_name', 'move_up_down_links')


@admin.register(IndicatorType)
class IndicatorTypeAdmin(OrderedModelAdmin):
    list_display = ('nombre', 'order', 'resumen', 'mostrar',
                    'series_red', 'series_nodos', 'series_federadores',
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
        indicator_type = IndicatorType.objects.get(pk=model_id)
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

    add_to_indexing_series = switch({'series_federadores': True})
    add_to_indexing_series.short_description = \
        'Agregar a las series de tiempo de nodos federadores'

    remove_from_indexing_series = switch({'series_federadores': False})
    remove_from_indexing_series.short_description = \
        'Quitar de las series de tiempo de nodos federadores'

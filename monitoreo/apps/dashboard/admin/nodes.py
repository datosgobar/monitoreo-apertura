# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from monitoreo.apps.dashboard.tasks import federate_catalogs
from monitoreo.apps.dashboard.models import HarvestingNode, FederationTask, \
    CentralNode

from utils import switch


@admin.site.register(HarvestingNode)
class HarvestingNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'enabled')
    actions = ('federate', 'enable', 'disable')

    enable = switch({'enabled': True})
    enable.short_description = 'Habilitar como nodo federador'

    disable = switch({'enabled': False})
    disable.short_description = 'Inhabilitar federacion del nodo'

    def federate(self, _, queryset):
        for harvesting_node in queryset:
            task = FederationTask.objects.create(
                harvesting_node=harvesting_node)
            federate_catalogs.delay(task)
    federate.short_description = 'Correr federacion'


admin.site.register(CentralNode, SingletonModelAdmin)

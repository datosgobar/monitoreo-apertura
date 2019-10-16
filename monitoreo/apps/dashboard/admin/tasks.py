# coding=utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django_datajsonar.admin.singleton_admin import SingletonAdmin
from django_datajsonar.admin.tasks import AbstractTaskAdmin

from monitoreo.apps.dashboard import models
from monitoreo.apps.dashboard.indicators_tasks import generate_indicators
from monitoreo.apps.dashboard.models.tasks import TasksConfig
from monitoreo.apps.dashboard.report_tasks import indicators_run, validation_run, \
    newly_report_run
from monitoreo.apps.dashboard.tasks import federate_catalogs


@admin.register(models.FederationTask)
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

        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "harvesting_node":
            kwargs["queryset"] = \
                models.HarvestingNode.objects.filter(enabled=True)
        return super(FederationAdmin, self)\
            .formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.IndicatorsGenerationTask)
class IndicatorTaskAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)
    exclude = ('node',)

    model = models.IndicatorsGenerationTask
    task = generate_indicators
    callable_str = 'monitoreo.apps.dashboard.indicators_tasks.indicators_run'


@admin.register(models.ReportGenerationTask)
class ReportAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = models.ReportGenerationTask
    task = indicators_run
    callable_str = 'monitoreo.apps.dashboard.report_tasks.send_reports'


@admin.register(models.ValidationReportTask)
class ValidationReportAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = models.ValidationReportTask
    task = validation_run
    callable_str = 'monitoreo.apps.dashboard.report_tasks.send_validations'


@admin.register(models.tasks.NewlyReportGenerationTask)
class NewlyReportGenerationTaskAdmin(AbstractTaskAdmin):
    readonly_fields = ('created', 'logs', 'status', 'finished')
    list_display = ('__unicode__',)

    model = models.tasks.NewlyReportGenerationTask
    task = newly_report_run
    callable_str = 'monitoreo.apps.dashboard.report_tasks.send_newly_reports'


@admin.register(TasksConfig)
class TaskConfigAdmin(SingletonAdmin):
    pass

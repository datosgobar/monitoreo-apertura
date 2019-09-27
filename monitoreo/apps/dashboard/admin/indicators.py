# coding=utf-8
from __future__ import unicode_literals

import django
from django.contrib import admin, messages
from django.conf.urls import url
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from import_export.forms import ImportForm

from django_datajsonar.admin.singleton_admin import SingletonAdmin

from monitoreo.apps.dashboard.management.import_utils import \
    invalid_indicators_csv, import_from_admin
from monitoreo.apps.dashboard.models.tasks import TasksTimeouts
from monitoreo.apps.dashboard.upload_handlers import \
    PersistentTemporaryFileUploadHandler
from monitoreo.apps.dashboard.views import indicators_csv
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, \
    IndicadorFederador


@method_decorator(csrf_exempt, name='import_action')
@method_decorator(csrf_protect, name='_import_action')
class CustomImportAdmin(ImportExportModelAdmin):
    formats = (base_formats.CSV,)

    def import_action(self, request, *args, **kwargs):
        request.upload_handlers = [
            PersistentTemporaryFileUploadHandler(request)
        ]
        return self._import_action(request, *args, **kwargs)

    def _import_action(self, request, *args, **kwargs):
        """
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """
        resource = self.get_import_resource_class()(
            **self.get_import_resource_kwargs(request, *args, **kwargs))

        context = {}

        import_formats = self.get_import_formats()
        form = ImportForm(import_formats,
                          request.POST or None,
                          request.FILES or None)

        context['title'] = "Import"
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in
                             resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name

        if request.POST and form.is_valid():
            model = self.model
            temp_file = form.cleaned_data['import_file']
            indicators_file = temp_file.temporary_file_path()
            import_from_admin.delay(indicators_file, model, request.user)
            return redirect(
                'admin:dashboard_' + model._meta.model_name + '_changelist')

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        return TemplateResponse(request, [self.import_template_name],
                                context)


class IndicatorResource(resources.ModelResource):
    class Meta:
        model = Indicador
        fields = export_order = (
            'fecha',
            'indicador_tipo',
            'indicador_valor',
            'jurisdiccion_nombre',
            'jurisdiccion_id',
        )


@admin.register(Indicador)
class IndicatorAdmin(CustomImportAdmin):
    list_filter = ('jurisdiccion_id',)
    resource_class = IndicatorResource

    def get_urls(self):
        urls = super(IndicatorAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<node_id>.+)/series-indicadores/$',
                          indicators_csv, name='node_series'), ]
        return extra_urls + urls


class IndexingIndicatorResource(resources.ModelResource):
    class Meta:
        model = IndicadorFederador
        fields = export_order = (
            'fecha',
            'indicador_tipo',
            'indicador_valor',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
        )


@admin.register(IndicadorFederador)
class IndexingIndicatorAdmin(CustomImportAdmin):
    list_filter = ('jurisdiccion_id',)
    resource_class = IndexingIndicatorResource

    def get_urls(self):
        urls = super(IndexingIndicatorAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<node_id>.+)/series-indicadores/$',
                          indicators_csv, name='indexing_series',
                          kwargs={'indexing': True}), ]
        return extra_urls + urls


class IndicadorRedResource(resources.ModelResource):
    class Meta:
        model = IndicadorRed
        fields = export_order = (
            'fecha',
            'indicador_tipo',
            'indicador_valor',
        )


@admin.register(IndicadorRed)
class IndicatorRedAdmin(CustomImportAdmin):
    resource_class = IndicadorRedResource

    def get_urls(self):
        urls = super(IndicatorRedAdmin, self).get_urls()
        extra_urls = [url(r'^series-indicadores/$', indicators_csv,
                          name='network_series'), ]
        return extra_urls + urls


@admin.register(TasksTimeouts)
class IndicatorConfigAdmin(SingletonAdmin):
    pass

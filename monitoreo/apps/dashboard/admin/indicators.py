# coding=utf-8
from __future__ import unicode_literals

from io import TextIOWrapper

import django
from django.contrib import admin, messages
from django.conf.urls import url
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.forms import ImportForm

from monitoreo.apps.dashboard.management.import_utils import \
    invalid_indicators_csv, import_indicators
from monitoreo.apps.dashboard.views import indicators_csv
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, \
    IndicadorFederador


class IndicatorResource(resources.ModelResource):
    class Meta:
        model = Indicador
        fields = export_order = (
            'fecha',
            'indicador_tipo__nombre',
            'indicador_valor',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
        )


@admin.register(Indicador)
class IndicatorAdmin(ImportExportModelAdmin):
    list_filter = ('jurisdiccion_id',)
    resource_class = IndicatorResource

    def get_urls(self):
        urls = super(IndicatorAdmin, self).get_urls()
        extra_urls = [url(r'^(?P<node_id>.+)/series-indicadores/$',
                          indicators_csv, name='node_series'), ]
        return extra_urls + urls

    def import_action(self, request, *args, **kwargs):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
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
            indicators_binary_file = form.cleaned_data['import_file']
            indicators_text_file = TextIOWrapper(indicators_binary_file)
            # Validación de datos
            if invalid_indicators_csv(indicators_text_file, model):
                msg = 'El csv de indicadores es inválido. ' \
                      'Correr el comando validate_indicators_csv para un ' \
                      'reporte detallado'
                messages.error(request, msg)
                return TemplateResponse(request, [self.import_template_name],
                                        context)
            indicators_text_file.seek(0)
            import_indicators.delay(indicators_binary_file, model)
            return redirect(
                'admin:dashboard_' + model._meta.model_name + '_changelist')

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        return TemplateResponse(request, [self.import_template_name],
                                context)


class IndexingIndicatorResource(resources.ModelResource):
    class Meta:
        model = IndicadorFederador
        fields = export_order = (
            'fecha',
            'indicador_tipo__nombre',
            'indicador_valor',
            'jurisdiccion_id',
            'jurisdiccion_nombre',
        )


@admin.register(IndicadorFederador)
class IndexingIndicatorAdmin(ImportExportModelAdmin):
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
            'indicador_tipo__nombre',
            'indicador_valor',
        )


@admin.register(IndicadorRed)
class IndicatorRedAdmin(ImportExportModelAdmin):
    resource_class = IndicadorRedResource

    def get_urls(self):
        urls = super(IndicatorRedAdmin, self).get_urls()
        extra_urls = [url(r'^series-indicadores/$', indicators_csv,
                          name='network_series'), ]
        return extra_urls + urls

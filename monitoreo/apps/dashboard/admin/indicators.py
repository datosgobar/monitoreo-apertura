# coding=utf-8
from __future__ import unicode_literals

import csv
from io import TextIOWrapper

import django
from django.contrib import admin
from django.conf.urls import url
from django.db import transaction
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.forms import ImportForm

from monitoreo.apps.dashboard.context_managers import suppress_autotime
from monitoreo.apps.dashboard.management.command_utils import \
    invalid_indicators_csv
from monitoreo.apps.dashboard.management.indicators_validator import \
    ValidationError
from monitoreo.apps.dashboard.views import indicators_csv
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed, \
    IndicadorFederador, IndicatorType


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

        if request.POST and form.is_valid():
            model = self.model
            indicators = []
            types_mapping = {ind_type.nombre: ind_type for
                             ind_type in IndicatorType.objects.all()}
            indicators_file = TextIOWrapper(form.cleaned_data['import_file'])
            # Validación de datos
            if invalid_indicators_csv(indicators_file, None):
                msg = 'El csv de indicadores es inválido. ' \
                      'Correr el comando validate_indicators_csv para un ' \
                      'reporte detallado'
                raise ValidationError(msg)
            indicators_file.seek(0)
            csv_reader = csv.DictReader(indicators_file)
            with suppress_autotime(model, ['fecha']):
                with transaction.atomic():
                    for row in csv_reader:
                        row['indicador_tipo'] = \
                            types_mapping[row.pop('indicador_tipo__nombre')]
                        filter_fields = {
                            field: row[field] for field in row if
                            field in ('fecha',
                                      'indicador_tipo',
                                      'jurisdiccion_id')
                        }
                        model.objects.filter(**filter_fields).delete()
                        indicators.append(model(**row))
                    model.objects.bulk_create(indicators)
                    return redirect('/')

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        context['title'] = "Import"
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in
                             resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
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

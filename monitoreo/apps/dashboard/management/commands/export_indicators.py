from __future__ import unicode_literals

import argparse

from import_export.resources import modelresource_factory

from django.core.management.base import BaseCommand

from monitoreo.apps.dashboard.models import IndicadorRed, Indicador
from monitoreo.apps.dashboard.admin.indicators import IndicadorRedResource, IndicatorResource


class Command(BaseCommand):
    help = """Toma el path a un csv de la forma
    [id, fecha, indicador_valor, indicador_tipo] para indicadores de red y
    [id, fecha, jurisdiccion_id, jurisdiccion_nombre, indicador_valor,
    indicador_tipo] para indicadores de nodos. Con esos datos crea o actualiza
    los rows de la base de datos correspondientes."""

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('w'))
        parser.add_argument('--aggregated', action='store_true')

    def handle(self, *args, **options):
        model = IndicadorRed if options['aggregated'] else Indicador
        model_resource = IndicadorRedResource if options['aggregated'] else IndicatorResource
        indicator_resource = modelresource_factory(model,
                                                   resource_class=model_resource)()
        result = indicator_resource.export()
        with options['file'] as export_csv:
            export_csv.write(result.csv)

# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from monitoreo.apps.dashboard.models import Indicador, IndicadorRed


def get_duplicates(model, distinct_fields, ignore_null=False):
    distinct = model.objects.all().distinct(*distinct_fields).values_list('pk', flat=True)
    duplicates = model.objects.all().exclude(pk__in=distinct)
    return duplicates


class Command(BaseCommand):
    help = """Borra indicadores de red y catálogo duplicados por día. 
    Apropos de: https://github.com/datosgobar/monitoreo-apertura/issues/109"""

    def add_arguments(self, parser):
        parser.add_argument('--ignore_null', action='store_true')

    def handle(self, *args, **options):
        duplicates = get_duplicates(IndicadorRed, ['fecha', 'indicador_tipo'])
        duplicates.delete()

        duplicates = get_duplicates(Indicador, ['fecha', 'indicador_tipo', 'jurisdiccion_nombre', 'jurisdiccion_id'])
        if options['ignore_null']:
            duplicates = duplicates.exclude(jurisdiccion_id=None)
        duplicates.delete()

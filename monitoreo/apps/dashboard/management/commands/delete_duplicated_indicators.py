# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = """Borra indicadores de red y catálogo duplicados por día.
    Apropos de: https://github.com/datosgobar/monitoreo-apertura/issues/109"""

    def add_arguments(self, parser):
        parser.add_argument('--ignore_null', action='store_true')

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM dashboard_indicadorred WHERE id NOT IN
                    ( SELECT MAX(id) FROM dashboard_indicadorred GROUP BY fecha, indicador_tipo_id );
                """)
            cursor.execute(
                """
                DELETE FROM dashboard_indicador WHERE jurisdiccion_id IS NOT NULL AND id NOT IN
                    ( SELECT MAX(id) FROM dashboard_indicador
                    GROUP BY fecha, indicador_tipo_id, jurisdiccion_nombre, jurisdiccion_id );
                """)

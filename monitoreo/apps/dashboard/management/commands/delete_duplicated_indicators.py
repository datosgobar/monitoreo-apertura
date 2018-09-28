# coding=utf-8
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.db import connection

from monitoreo.apps.dashboard.models import Indicador, IndicadorRed


def delete_duplicates(model, distinct_fields, ignore_null=False):

    columns = ", ".join(distinct_fields)
    table = model._meta.db_table
    null_condition = ' AND jurisdiccion_id IS NOT NULL' if ignore_null else ''

    query = """
        DELETE FROM %s
        WHERE id NOT IN
        (
            SELECT id FROM %s GROUP BY %s
        )%s;
        """ % (table, table, columns, null_condition)

    with connection.cursor() as cursor:
        cursor.execute(query)


class Command(BaseCommand):
    help = """Borra indicadores de red y catálogo duplicados por día.
    Apropos de: https://github.com/datosgobar/monitoreo-apertura/issues/109"""

    def add_arguments(self, parser):
        parser.add_argument('--ignore_null', action='store_true')

    def handle(self, *args, **options):
        delete_duplicates(IndicadorRed, ['fecha', 'indicador_tipo_id'])

        delete_duplicates(Indicador,
                          ['fecha', 'indicador_tipo_id', 'jurisdiccion_nombre', 'jurisdiccion_id'],
                          options['ignore_null'])

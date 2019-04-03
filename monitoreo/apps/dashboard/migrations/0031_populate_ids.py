# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-10 13:01
from __future__ import unicode_literals

from django.db import migrations

title_to_id_map = {
    'Ministerio de Desarrollo Social': 'desarrollo-social',
    'Datos de la Jefatura de Gabinete de Minsitros': 'jgm',
    'Datos Programación Microeconómica': 'sspmi',
    'Datos abiertos de turismo - Plataforma YVERA': 'turismo',
    'Ministerio de Desarrollos Social': 'desarrollo-social',
    'DATOS DEL MINISTERIO DE AMBIENTE DE LA NACIÓN': 'ambiente',
    'Datos PPN': 'procuracion-penitenciaria',
    'DatosMINEM': 'minem'
}


def fill_indicators_id(apps, schema_editor):
    Indicador = apps.get_model("dashboard", "Indicador")
    for title, identifier in title_to_id_map.items():
        Indicador.objects.filter(jurisdiccion_nombre=title).update(jurisdiccion_id=identifier)
        print(u"Migrados los indicadores de {}".format(identifier))


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('dashboard', '0030_reportgenerationtask'),
    ]

    operations = [
        migrations.RunPython(fill_indicators_id, migrations.RunPython.noop),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def convert_callable_str(apps, _schema_editor):
    stage_model = apps.get_model('django_datajsonar', 'Stage')
    stages = stage_model.objects.filter(callable_str__contains=".tasks.")
    for stage in stages:
        stage.callable_str = stage.callable_str.replace(".tasks.", ".federation_tasks.")
        stage.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0057_federation_task_callable_str_migration'),
    ]

    operations = [
        migrations.RunPython(convert_callable_str, migrations.RunPython.noop)
    ]

from __future__ import unicode_literals

from django.db import migrations

from monitoreo.apps.dashboard.normalization_utils import normalize_node_indicator_values, \
    normalize_network_indicator_values, normalize_federator_indicator_values


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0055_auto_20191030_1544'),
    ]

    operations = [
        migrations.RunPython(normalize_node_indicator_values,
                             migrations.RunPython.noop),
        migrations.RunPython(normalize_network_indicator_values,
                             migrations.RunPython.noop),
        migrations.RunPython(normalize_federator_indicator_values,
                             migrations.RunPython.noop),
    ]
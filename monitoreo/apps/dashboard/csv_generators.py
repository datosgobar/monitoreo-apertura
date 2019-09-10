import os

from django.conf import settings
from django_datajsonar.models import Node

from monitoreo.apps.dashboard.helpers import generate_time_series
from monitoreo.apps.dashboard.models.nodes import HarvestingNode
from monitoreo.apps.dashboard.models.indicators import IndicadorRed, Indicador,\
    IndicadorFederador


class IndicatorSeriesCSVGenerator:
    base_dir = os.path.join(settings.MEDIA_ROOT, 'indicator_files')

    def generate_network_time_series_files(self):
        os.makedirs(self.base_dir, exist_ok=True)
        queryset = IndicadorRed.objects.all()
        self._write_series_file('red', self.base_dir, queryset)

    def generate_nodes_time_series_files(self):
        self._generate_model_series(
            'nodes', Node, Indicador)

    def generate_federator_nodes_time_series_files(self):
        self._generate_model_series(
            'federator-nodes', HarvestingNode, IndicadorFederador)

    def _generate_model_series(self, dst, node_model, indicator_model):
        dst_dir = os.path.join(self.base_dir, dst)
        os.makedirs(dst_dir, exist_ok=True)
        for node in node_model.objects.all():
            queryset = indicator_model.objects. \
                filter(jurisdiccion_id=node.catalog_id)
            self._write_series_file(node.catalog_id, dst_dir, queryset)

    def _write_series_file(self, identifier, dst_dir, queryset):
        filename = f'indicadores-{identifier}-series.csv'
        with open(os.path.join(dst_dir, filename), 'w') \
                as dst_file:
            generate_time_series(queryset, dst_file)

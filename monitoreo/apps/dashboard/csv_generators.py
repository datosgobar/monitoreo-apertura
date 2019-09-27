import os

from django_datajsonar.models import Node

from monitoreo.apps.dashboard.helpers import generate_time_series
from monitoreo.apps.dashboard.indicators_dir_manager import IndicatorsDirManager
from monitoreo.apps.dashboard.models.nodes import HarvestingNode
from monitoreo.apps.dashboard.models.indicators import IndicadorRed, Indicador, IndicadorFederador


class IndicatorSeriesCSVGenerator:
    dir_manager = IndicatorsDirManager()

    def generate_network_time_series_files(self):
        queryset = IndicadorRed.objects.all()
        dst_dir = self.dir_manager.get_network_indicators_dir()
        self._write_series_file('red', dst_dir, queryset)

    def generate_nodes_time_series_files(self):
        dst_dir = self.dir_manager.get_node_indicators_dir()
        self._generate_model_series(dst_dir, Node, Indicador)

    def generate_federator_nodes_time_series_files(self):
        dst_dir = self.dir_manager.get_federator_indicators_dir()
        self._generate_model_series(dst_dir, HarvestingNode, IndicadorFederador)

    def _generate_model_series(self, dst_dir, node_model, indicator_model):
        for node in node_model.objects.all():
            queryset = indicator_model.objects.filter(jurisdiccion_id=node.catalog_id)
            self._write_series_file(node.catalog_id, dst_dir, queryset)

    def _write_series_file(self, identifier, dst_dir, queryset):
        filename = f'indicadores-{identifier}-series.csv'
        with open(os.path.join(dst_dir, filename), 'w') as dst_file:
            generate_time_series(queryset, dst_file)

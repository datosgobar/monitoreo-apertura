import gzip
import os

from monitoreo.apps.dashboard.custom_generators import csv_panel_writer
from monitoreo.apps.dashboard.indicators_dir_manager import IndicatorsDirManager
from monitoreo.apps.dashboard.models import IndicadorRed, IndicadorFederador, Indicador


class IndicatorCSVZipGenerator:
    dir_manager = IndicatorsDirManager()

    def generate_network_panel_zip(self):
        fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
        dst_dir = self.dir_manager.get_network_indicators_dir()
        self._write_zip_file('red', dst_dir, IndicadorRed, fieldnames)

    def generate_node_panel_zip(self):
        fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
        dst_dir = self.dir_manager.get_node_indicators_dir()
        self._write_zip_file('nodos', dst_dir, Indicador, fieldnames)

    def generate_federator_node_panel_zip(self):
        fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
        dst_dir = self.dir_manager.get_federator_indicators_dir()
        self._write_zip_file('nodos-federadores', dst_dir, IndicadorFederador, fieldnames)

    def _write_zip_file(self, domain, dst_dir, model, values_lookup):
        filename = f'indicadores-{domain}.csv.gz'
        with gzip.open(os.path.join(dst_dir, filename), 'wt') as zipfile:
            for row in csv_panel_writer(model, values_lookup):
                zipfile.write(row)

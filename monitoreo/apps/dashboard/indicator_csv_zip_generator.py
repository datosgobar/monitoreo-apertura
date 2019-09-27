import gzip
import os

from monitoreo.apps.dashboard.custom_generators import csv_panel_writer
from monitoreo.apps.dashboard.indicators_dir_manager import IndicatorsDirManager
from monitoreo.apps.dashboard.models import IndicadorRed


class IndicatorCSVZipGenerator:
    dir_manager = IndicatorsDirManager()

    def generate_network_panel_zip(self):
        fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
        dst_dir = self.dir_manager.get_network_indicators_dir()
        self._write_zip_file('red', dst_dir, IndicadorRed, fieldnames)

    def generate_node_panel_zip(self):
        fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
        dst_dir = self.dir_manager.get_network_indicators_dir()
        self._write_zip_file('red', dst_dir, IndicadorRed, fieldnames)

    def generate_federator_node_panel_zip(self):
        fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor', 'jurisdiccion_nombre', 'jurisdiccion_id']
        dst_dir = self.dir_manager.get_network_indicators_dir()
        self._write_zip_file('red', dst_dir, IndicadorRed, fieldnames)

    def _write_zip_file(self, identifier, dst_dir, model, values_lookup):
        filename = f'indicadores-{identifier}.csv.zip'
        with gzip.open(os.path.join(dst_dir, filename), 'w') as zipfile:
            for row in csv_panel_writer(model, values_lookup):
                zipfile.write(row)

#! coding: utf-8

from pydatajson import DataJson
from .reader import SpreadsheetReader

# Valores numéricos de las filas en la hoja de distribuciones del PAD
COMPROMISO = 1
DATAJSON = 8
DATASET = 9
DISTRIBUCION = 13


class PADIndicators:
    def __init__(self, reader=SpreadsheetReader, data_json=DataJson):
        """Clase que calcula los indicadores del PAD.

        Args:
            reader: Clase lectora de planillas.
            data_json: Clase lectora de metadatos .json de los catálogos.
        """

        self.reader = reader()
        self.data_json = data_json()
        self.datajson_cache = {}

    def generate_pad_indicators(self, spreadsheet_id):
        """Genera indicadores del PAD, con varios datos sobre el estado de
        las distribuciones y los compromisos.

        Args:
            spreadsheet_id (str): ID de la hoja de datos del PAD sobre la
            cual leer y calcular los indicadores.

        Returns:
            dict: diccionario con los indicadores como claves
        """

        sheet = self.reader.read_sheet(spreadsheet_id)
        indicators = {}
        indicators.update(self.generate_documentation_indicators(sheet))
        return indicators

    def generate_documentation_indicators(self, sheet):
        """Genera los indicadores de documentación. Un compromiso es
        considerado como documentado cuando:
            1. todas sus distribuciones tienen asociado un data.json
            2. los datasets y distribuciones asociadas al compromiso existen
            dentro de ese data.json
            3. la metadata de los datasets del compromiso en el data.json pasan
            la validación de la librería pydatajson
        Args:
            sheet (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos documentados
                (cantidad y porcentaje)
        """
        count = 0
        documented = 0
        for compromiso in sheet:
            count += 1
            if self.compromiso_is_documented(compromiso):
                documented += 1

        documented_pct = round(float(documented) / count, 2) * 100

        documented_indicators = {
            'pad_items_documentados_cant': documented,
            'pad_items_no_documentados_cant': count - documented,
            'pad_items_documentados_pct': documented_pct
        }
        return documented_indicators

    def compromiso_is_documented(self, compromiso):
        """Verifica si un compromiso está documentado. Un compromiso se
        considera documentado si:
            1. Para cada dataset, su campo 'catalog_datajson_url' apunta a un
            data.json válido
            2. Todos sus datasets están dentro del data.json asociado
            3. Los datasets dentro del data.json pasan la validación de
            'pydatajson'

        Args:
            compromiso (dict): compromiso a validar

        Returns:
            bool: True si el compromiso está documentado, False caso contrario
        """
        for dataset in compromiso['dataset']:
            datajson_url = dataset.get('catalog_datajson_url')
            if not datajson_url:  # Falta un datajson, no está documentado
                return False

            # Para no descargar y leer el mismo catálogo varias veces se lo
            # guarda en una variable de clase junto con su validación
            if datajson_url not in self.datajson_cache:
                self.datajson_cache[datajson_url] = \
                    self.data_json.validate_catalog(datajson_url)

            validation = self.datajson_cache[datajson_url]['error']['dataset']
            dataset_title = dataset['dataset_title']
            found = False
            for datajson_dataset in validation:
                if datajson_dataset['title'] == dataset_title:
                    if datajson_dataset['status'] != 'OK':
                        return False
                    found = True

            if not found:  # El dataset no está en el data.json
                return False

        return True

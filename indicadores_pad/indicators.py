#! coding: utf-8
import requests
from pydatajson import DataJson
from indicadores_pad.reader import SpreadsheetReader
# Valores numéricos de las filas en la hoja de distribuciones del PAD
COMPROMISO = 1
DATAJSON = 8
DATASET = 9
DISTRIBUCION = 13


class PADIndicators:
    def __init__(self, reader=SpreadsheetReader(), data_json=DataJson()):
        """Clase que calcula los indicadores del PAD.

        Args:
            reader: instancia de objeto lector de planillas.
            data_json: instancia de lector de metadatos .json de los catálogos.
        """

        self.reader = reader
        self.data_json = data_json
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
        indicators.update(self.generate_license_indicators(sheet))
        indicators.update(self.generate_download_indicators(sheet))
        indicators.update(self.generate_frequency_indicator(sheet))
        indicators.update(self.generate_format_indicator(sheet))
        return indicators

    @staticmethod
    def generate_format_indicator(sheet):
        """Genera el indicador de formatos: un diccionario que cuenta los
        formatos presentes de las distribuciones dentro del PAD
        
        Args:
            sheet(list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: Diccionario con los formatos como claves y la cantidad de
                cada uno como valores
        """
        formats = {}
        for compromiso in sheet:
            for dataset in compromiso.get('dataset', []):
                for distribution in dataset.get('distribution', []):
                    distrib_format = distribution.get('distribution_format')
                    if distrib_format:
                        formats[distrib_format] = \
                            formats.get(distrib_format, 0) + 1
        return {
            'pad_distributions_formatos_cant': formats
        }

    @staticmethod
    def generate_frequency_indicator(sheet):
        """Genera el indicador de frecuencia: Un diccionario que cuenta las
        periodicidades de actualización de todas las distribuciones dentro del
        PAD
        
        Args:
            sheet (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: Diccionario con las frecuencias como claves y la cantidad de
                cada una como valores
        """

        frequencies = {}
        for compromiso in sheet:
            for dataset in compromiso['dataset']:
                periodicity = dataset.get('dataset_accrualPeriodicity')
                if periodicity:
                    frequencies[periodicity] = \
                        frequencies.get(periodicity, 0) + 1

        return {
            'pad_datasets_frecuencia_cant': frequencies
        }

    def generate_download_indicators(self, sheet):
        """Genera los indicadores de descarga. Un compromiso se considera como
        descargable si todas sus distribuciones tienen un link válido de
        descarga en el campo 'distribution_downloadURL
        
        Args:
            sheet (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos descargables
                (cantidad y porcentaje)
        """
        count = 0
        downloadable = 0
        for compromiso in sheet:
            count += 1
            if self.compromiso_is_downloadable(compromiso):
                downloadable += 1

        downloadable_pct = round(float(downloadable) / count * 100, 2)
        license_indicators = {
            'pad_items_descarga_cant': downloadable,
            'pad_items_no_descarga_cant': count - downloadable,
            'pad_items_descarga_pct': downloadable_pct
        }
        return license_indicators

    @staticmethod
    def compromiso_is_downloadable(compromiso):
        """Verifica que un compromiso sea descargable. Se lo consierará como
        descargable si todas sus distribuciones tienen un link válido en el
        campo 'distribution_downloadURL', es decir que el request de 200
        
        Args:
            compromiso (dict): compromiso obtenido de la lectura de la planilla
                de cálculo del PAD
        Returns:
            bool: True si el compromiso es descargable, False caso contrario
        """

        for dataset in compromiso['dataset']:
            distributions = dataset.get('distribution')
            if not distributions:
                return False

            for distribution in distributions:
                try:
                    # Pido el header a la URL de descarga
                    response = requests.head(
                        distribution.get('distribution_downloadURL'))
                    if response.status_code != 200:
                        return False
                except (requests.ConnectionError,
                        requests.models.MissingSchema):
                    # No se pudo establecer una conexión
                    return False
        return True

    def generate_license_indicators(self, sheet):
        """Genera los indicadores de licencia. Un compromiso es
        considerado como licenciado cuando todos sus datasets asociadas 
        tienen algún valor en el campo dataset_license
        
        Args:
            sheet (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos licenciados
                (cantidad y porcentaje)
        """
        count = 0
        licensed = 0
        for compromiso in sheet:
            count += 1
            if self.compromiso_is_licensed(compromiso):
                licensed += 1

        licensed_pct = round(float(licensed) / count * 100, 2)
        license_indicators = {
            'pad_items_licencia_cant': licensed,
            'pad_items_sin_licencia_cant': count - licensed,
            'pad_items_licencia_pct': licensed_pct
        }
        return license_indicators

    @staticmethod
    def compromiso_is_licensed(compromiso):
        """Verifica si un compromiso está licenciado. Se lo considerará como
        licenciado a un compromiso si todos sus datasets asociadas tienen algún
        valor en el campo 'dataset_license'
        
        Args:
            compromiso (dict): compromiso obtenido de la lectura de la planilla
                de cálculo del PAD
        Returns:
            bool: True si el compromiso está licenciado, False caso contrario
        """

        for dataset in compromiso['dataset']:
            # Chequeo campo existente y no falso (i.e. distinto de string vacío)
            if not dataset.get('dataset_license') or \
                    not dataset['dataset_license']:
                return False
        return True

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

        documented_pct = round(float(documented) / count * 100, 2)

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

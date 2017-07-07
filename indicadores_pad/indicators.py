#! coding: utf-8
import requests
from pydatajson import DataJson, parse_repeating_time_interval
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

        indicators = {}
        sheet = self.reader.read_sheet(spreadsheet_id)
        for jurisdiccion, compromisos in sheet.items():
            indicators[jurisdiccion] = {}

            indicators[jurisdiccion].update(
                self.generate_documentation_indicators(compromisos))
            indicators[jurisdiccion].update(
                self.generate_license_indicators(compromisos))
            indicators[jurisdiccion].update(
                self.generate_download_indicators(compromisos))
            indicators[jurisdiccion].update(
                self.generate_frequency_indicator(compromisos))
            indicators[jurisdiccion].update(
                self.generate_format_indicator(compromisos))
            indicators[jurisdiccion].update(
                self.generate_update_indicators(compromisos))

            indicators[jurisdiccion].update({
                'pad_compromisos_cant': len(compromisos)
            })
        # Indicadores de la planilla entera
        network_indics = self.generate_network_indicators(indicators)
        network_indics.update(self.generate_count_indicators(spreadsheet_id))
        network_indics.update({
            'pad_distribuciones_cant': self.count_distributions(sheet)
        })


        return indicators, network_indics

    @staticmethod
    def count_distributions(sheet):
        distribution_count = 0
        for jurisdiccion in sheet.values():
            for compromiso in jurisdiccion:
                for dataset in compromiso.get('dataset', []):
                    distribution_count += len(dataset.get('distribution', []))
        return distribution_count

    @staticmethod
    def generate_network_indicators(indicators):
        """Suma los indicadores de cada jurisdicción para generar los
        indicadores agregados de la planilla entera del PAD.
        
        Args:
            indicators (dict): Diccionario con los indicadores desagregados
                calculados con los métodos 'generate_'
        
        Returns:
            dict: diccionario con los indicadores sumados
        """
        network_indicators = {}
        for indics in indicators.values():
            network_indicators = add_dicts(network_indicators, indics)

        # Recalculo los porcentajes
        doc_total = network_indicators['pad_items_documentados_cant'] + \
            network_indicators['pad_items_no_documentados_cant']
        doc_pct = float(network_indicators['pad_items_documentados_cant']) / \
            doc_total * 100
        network_indicators['pad_items_documentados_pct'] = round(doc_pct, 2)

        lic_total = network_indicators['pad_items_licencia_cant'] + \
            network_indicators['pad_items_sin_licencia_cant']
        lic_pct = float(network_indicators['pad_items_licencia_cant']) / \
            lic_total * 100
        network_indicators['pad_items_licencia_pct'] = round(lic_pct, 2)

        down_total = network_indicators['pad_items_descarga_cant'] + \
            network_indicators['pad_items_no_descarga_cant']
        down_pct = float(network_indicators['pad_items_descarga_cant']) / \
            down_total * 100
        network_indicators['pad_items_descarga_pct'] = round(down_pct, 2)

        up_total = network_indicators['pad_items_actualizados_cant'] + \
            network_indicators['pad_items_desactualizados_cant']
        up_pct = float(network_indicators['pad_items_actualizados_cant']) / \
            up_total * 100
        network_indicators['pad_items_actualizados_pct'] = round(up_pct, 2)

        return network_indicators

    def generate_count_indicators(self, spreadsheet):
        """Genera dos indicadores: cantidad de items y de jurisdicciones de 
        la planilla entera"""

        count = self.reader.count_compromisos(spreadsheet)
        result = {
            'pad_compromisos_cant': count['compromisos_cant'],
            'pad_jurisdicciones_cant': count['jurisdicciones_cant']
        }
        return result

    def generate_update_indicators(self, compromisos):
        """Genera los indicadores de actualización."""

        count = 0
        updated = 0
        for compromiso in compromisos:
            count += 1
            if self.compromiso_is_updated(compromiso):
                updated += 1

        updated_pct = round(float(updated) / count * 100, 2)

        updated_indicators = {
            'pad_items_actualizados_cant': updated,
            'pad_items_desactualizados_cant': count - updated,
            'pad_items_actualizados_pct': updated_pct
        }
        return updated_indicators

    def dataset_is_updated(self, dataset):
        """Evalúa si el dataset figura como actualizado dentro de los metadatos
        de su catálogo asociado. Devuelve True en ese caso, o si no tiene un
        catálogo asociado.
        """

        catalog = dataset.get('catalog_datajson_url')
        if not catalog:
            return True

        return self.data_json.dataset_is_updated(catalog, dataset.get(
            'dataset_title'))

    def compromiso_is_updated(self, compromiso):
        """Verifica que un compromiso esté actualizado. Un compromiso se
        considera como actualizado si hay al menos una distribución cuyo 
        dataset_accrualPeriodicity es de igual o menor agregación temporal que 
        compromiso_actualizacion
        
        Args:
            compromiso (dict): compromiso obtenido de la lectura de la planilla
                de cálculo del PAD
        Returns:
            bool: True si el compromiso es descargable, False caso contrario
        """
        periodicity = compromiso.get('compromiso_actualizacion', '')
        for dataset in compromiso.get('dataset', []):
            dataset_periodicity = dataset.get('dataset_accrualPeriodicity', '')
            if self.compare_accrual_periodicity(dataset_periodicity,
                                                periodicity):
                return self.dataset_is_updated(dataset)

        return False

    @staticmethod
    def compare_accrual_periodicity(periodicity, other):
        """Devuelve true si 'periodicity' es de menor o igual período que
        'other'
        
        Args:
            periodicity (str): periodicity ISO 8601, por ejemplo 'R/P1Y' para
                período anual.
            other (str): periodicity ISO 8601, por ejemplo 'R/P1Y' para
                período anual.
        Returns:
            bool: True si periodicity es mayor o igual que other, False caso
                contrario. Devuelve False si alguno de los argumentos tiene un
                formato inválido.
        """

        periodicity = parse_repeating_time_interval(periodicity)
        other = parse_repeating_time_interval(other)

        if not periodicity or not other:
            return False

        return periodicity <= other

    @staticmethod
    def generate_format_indicator(compromisos):
        """Genera el indicador de formatos: un diccionario que cuenta los
        formatos presentes de las distribuciones dentro del PAD
        
        Args:
            compromisos (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: Diccionario con los formatos como claves y la cantidad de
                cada uno como valores
        """
        formats = {}
        for compromiso in compromisos:
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
    def generate_frequency_indicator(compromisos):
        """Genera el indicador de frecuencia: Un diccionario que cuenta las
        periodicidades de actualización de todas las distribuciones dentro del
        PAD
        
        Args:
            compromisos (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: Diccionario con las frecuencias como claves y la cantidad de
                cada una como valores
        """

        frequencies = {}
        for compromiso in compromisos:
            for dataset in compromiso.get('dataset', []):
                periodicity = dataset.get('dataset_accrualPeriodicity')
                if periodicity:
                    frequencies[periodicity] = \
                        frequencies.get(periodicity, 0) + 1

        return {
            'pad_datasets_frecuencia_cant': frequencies
        }

    def generate_download_indicators(self, compromisos):
        """Genera los indicadores de descarga. Un compromiso se considera como
        descargable si todas sus distribuciones tienen un link válido de
        descarga en el campo 'distribution_downloadURL
        
        Args:
            compromisos (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos descargables
                (cantidad y porcentaje)
        """
        count = 0
        downloadable = 0
        for compromiso in compromisos:
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

        for dataset in compromiso.get('dataset', []):
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

    def generate_license_indicators(self, compromisos):
        """Genera los indicadores de licencia. Un compromiso es
        considerado como licenciado cuando todos sus datasets asociadas 
        tienen algún valor en el campo dataset_license
        
        Args:
            compromisos (list): lista de dicts de una spreadsheet ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos licenciados
                (cantidad y porcentaje)
        """
        count = 0
        licensed = 0
        for compromiso in compromisos:
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

        for dataset in compromiso.get('dataset', []):
            # Chequeo campo existente y no falso (i.e. distinto de string vacío)
            if not dataset.get('dataset_license') or \
                    not dataset['dataset_license']:
                return False
        return True

    def generate_documentation_indicators(self, compromisos):
        """Genera los indicadores de documentación. Un compromiso es
        considerado como documentado cuando:
            1. todas sus distribuciones tienen asociado un data.json
            2. los datasets y distribuciones asociadas al compromiso existen
            dentro de ese data.json
            3. la metadata de los datasets del compromiso en el data.json pasan
            la validación de la librería pydatajson
        Args:
            compromisos (list): lista de dicts de compromisos ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos documentados
                (cantidad y porcentaje)
        """
        count = 0
        documented = 0
        for compromiso in compromisos:
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
        for dataset in compromiso.get('dataset', []):
            datajson_url = dataset.get('catalog_datajson_url')
            if not datajson_url:  # Falta un datajson, no está documentado
                return False

            # Para no descargar y leer el mismo catálogo varias veces se lo
            # guarda en una variable de clase junto con su validación
            if datajson_url not in self.datajson_cache:
                self.datajson_cache[datajson_url] = \
                    self.data_json.validate_catalog(datajson_url)

            validation = self.datajson_cache[datajson_url]['error']['dataset']
            dataset_title = dataset.get('dataset_title')
            found = False
            for datajson_dataset in validation:
                if datajson_dataset['title'] == dataset_title:
                    if datajson_dataset['status'] != 'OK':
                        return False
                    found = True

            if not found:  # El dataset no está en el data.json
                return False

        return True


def add_dicts(one_dict, other_dict):
    """Suma clave a clave los dos diccionarios. Si algún valor es un
    diccionario, llama recursivamente a la función. Ambos diccionarios deben
    tener exactamente las mismas claves, y los valores asociados deben ser
    sumables, o diccionarios.

    Args:
        one_dict (dict)
        other_dict (dict)

    Returns:
        dict: resultado de la suma
    """
    result = other_dict.copy()
    for k, v in one_dict.items():
        if isinstance(v, dict):
            result[k] = add_dicts(v, other_dict.get(k, {}))
        else:
            result[k] = result.get(k, 0) + v

    return result

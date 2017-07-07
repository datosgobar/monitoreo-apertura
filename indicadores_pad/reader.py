#! coding: utf-8
from __future__ import print_function

import google_drive


class SpreadsheetReader:
    # Valores numéricos de las filas en la hoja de distribuciones del PAD
    JURISDICCION = 2
    COMPROMISO = 1
    DATAJSON = 8
    DATASET = 9
    DISTRIBUCION = 13

    def __init__(self):
        self.jurisdicciones = []
        self.sheet = ""

    def read_sheet(self, sheet_id):
        """Lee la hoja completa del estado del Plan de Apertura de datos,
        y la parsea en diccionario de Python.

        Args:
            sheet_id (str): ID de una hoja de google drive con los valores del
                PAD

        Returns:
            dict: diccionario con el formato especificado
        """

        if isinstance(sheet_id, dict):
            return sheet_id
        if isinstance(sheet_id, (str, unicode)):
            if self.sheet == sheet_id:  # Ya fue leída la misma hoja
                return self.jurisdicciones
            sheet = google_drive.get_sheet(sheet_id, "pad_distribuciones")
            self.sheet = sheet_id
        else:
            raise TypeError('Valor de "sheet" inválido. Se esperaba tipo dict o'
                            ' str, recibido {}'.format(type(sheet_id)))

        self.jurisdicciones = {}
        # compromisos: claves los IDs de cada compromiso, valores una lista
        # de los data.json asociados a sus distribuciones
        header = sheet[0]
        for row in sheet[1:]:  # Índice 0 es el header de la tabla
            # Asumo que cuando la len es baja, ya son rows inválidos
            if len(row) <= self.DATASET:
                continue

            jurisdiccion_nombre = row[self.JURISDICCION]
            if jurisdiccion_nombre not in self.jurisdicciones:
                self.jurisdicciones[jurisdiccion_nombre] = []

            compromiso_id = row[self.COMPROMISO]
            compromiso = self.get_or_create_compromiso(compromiso_id,
                                                       jurisdiccion_nombre)

            dataset_title = row[self.DATASET]
            dataset = self.get_or_create_dataset(dataset_title, compromiso)

            # Cada row representa una distribución única, cargamos los datos y
            # la agregamos al dataset
            distribution = {}
            dataset['distribution'].append(distribution)
            for name in header:
                index = header.index(name)
                value = row[index] if len(row) > index else ""
                if 'compromiso' in name or 'jurisdiccion' in name:
                    compromiso[name] = value
                elif 'dataset' in name or 'catalog' in name:
                    dataset[name] = value
                else:  # Valores de 'distribution'
                    distribution[name] = value
        return self.jurisdicciones

    @staticmethod
    def get_or_create_dataset(dataset_title, compromiso):
        """Devuelve el dataset perteneciente a 'compromiso' con el título
        'dataset_title', o de no existir, lo crea y lo agrega a los datasets del
        compromiso.
        Args:
            dataset_title (str): valor del campo 'dataset_title' en el dataset a
                buscar.
            compromiso (dict): diccionario representando a un compromiso, con el
                formato devuelto por la función 'get_or_create_compromiso',
                es decir con una clave 'dataset' con valor de lista
        Returns:
            dict: diccionario representante del dataset:
                {
                    'dataset_title': dataset_title,
                    distribution: [],
                }
        """
        for dataset in compromiso['dataset']:
            if dataset['dataset_title'] == dataset_title:
                return dataset

        dataset = {
            'dataset_title': dataset_title,
            'distribution': []
        }
        compromiso['dataset'].append(dataset)
        return dataset

    def get_or_create_compromiso(self, compromiso_id, jurisdiccion):
        """Devuelve el compromiso con 'compromiso_id' en la lista 'compromisos',
        o de no existir, lo crea y lo agrega a 'compromisos'.
        Args:
            compromiso_id (str): ID del compromiso a buscar.

        Returns:
            dict: compromiso con el campo compromiso_id correspondiente
        """
        for compromiso in self.jurisdicciones[jurisdiccion]:
            if compromiso['compromiso_id'] == compromiso_id:
                return compromiso

        compromiso = {
            'compromiso_id': compromiso_id,
            'dataset': []
        }
        self.jurisdicciones[jurisdiccion].append(compromiso)
        return compromiso


def main():
    import json
    spreadsheet_id = '1uG68Yq9z1l6IX1kW8A3uO9yGHSNqDglFuagk7BxKOaw'
    spreadsheet = SpreadsheetReader()
    print(json.dumps(spreadsheet.read_sheet(spreadsheet_id), indent=4))
    spreadsheet.read_sheet(spreadsheet_id)

if __name__ == '__main__':
    main()

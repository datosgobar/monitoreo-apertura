#! coding: utf-8

import reader
from pydatajson import DataJson

# Valores numéricos de las filas en la hoja de distribuciones del PAD
COMPROMISO = 1
DATAJSON = 8
DATASET = 9
DISTRIBUCION = 13


class PADIndicators:
    def __init__(self):
        self.dj = DataJson()

    @staticmethod
    def count_rows(spreadsheet_id, sheet):
        # Trae la sheet entera
        rows = reader.read_sheet(spreadsheet_id)
        return len(rows)

    def generate_pad_indicators(self, spreadsheet_id):
        """Genera indicadores del PAD, con varios datos sobre el estado de
        las distribuciones y los compromisos.
        
        Args:
            spreadsheet_id (str): ID de la hoja de datos del PAD sobre la 
            cual leer y calcular los indicadores.
        
        Returns:
            dict: diccionario con los indicadores como claves
        """

        rows = reader.read_sheet(spreadsheet_id)

    def generate_documentation_indicators(self, sheet):
        """Genera los indicadores de documentación. Un compromiso es 
        considerado como documentado cuando:
            1. todas sus distribuciones tienen asociado un data.json
            2. los datasets y distribuciones asociadas al compromiso existen 
            dentro de ese data.json
            3. la metadata de los datasets del compromiso en el data.json pasan 
            la validación de la librería pydatajson
        Args:
            sheet (str o list): ID de un spreadsheet de google docs o una 
                lista de filas de una spreadsheet ya parseada
        Returns:
            dict: diccionario con indicadores de compromisos documentados
                (cantidad y porcentaje)
        """

        if isinstance(sheet, str):
            sheet = reader.get_sheet(sheet, "pad_distribuciones")

        # compromisos: claves los IDs de cada compromiso, valores una lista
        # de los data.json asociados a sus distribuciones
        compromisos = {}
        for row in sheet:
            compromiso_id = row[COMPROMISO]
            if compromiso_id not in compromisos:
                compromisos[compromiso_id] = []

            if row[DATAJSON] not in compromisos[compromiso_id]:
                compromisos[compromiso_id].append(row[DATAJSON])

            ## Incomplete
            if row[DATASET] not in compromisos[compromiso_id]:
                pass
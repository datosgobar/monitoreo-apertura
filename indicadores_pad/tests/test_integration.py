#! coding: utf-8

import unittest
from indicadores_pad.indicators import PADIndicators


class PADTest(unittest.TestCase):
    spreadsheet = '1uG68Yq9z1l6IX1kW8A3uO9yGHSNqDglFuagk7BxKOaw'

    def setUp(self):
        self.pad = PADIndicators()
        self.indics, self.network_indics = \
            self.pad.generate_pad_indicators(self.spreadsheet)

    def test_count_indicators_add_up_to_the_same(self):
        for k, jurisdiccion in self.indics.items():
            doc_count = jurisdiccion['pad_items_documentados_cant'] + \
                jurisdiccion['pad_items_no_documentados_cant']

            lic_count = jurisdiccion['pad_items_licencia_cant'] + \
                jurisdiccion['pad_items_sin_licencia_cant']

            self.assertEqual(doc_count, lic_count)

            update_count = jurisdiccion['pad_items_actualizados_cant'] + \
                jurisdiccion['pad_items_desactualizados_cant']

            self.assertEqual(doc_count, update_count)

            download_count = jurisdiccion['pad_items_descarga_cant'] + \
                jurisdiccion['pad_items_no_descarga_cant']

            self.assertEqual(doc_count, download_count)

    def test_count_indicators(self):
        jurisdictions = self.network_indics['pad_jurisdicciones_cant']
        compromisos = self.network_indics['pad_compromisos_cant']

        compromisos_actual = 0
        for indicators in self.indics.values():
            compromisos_actual += indicators['pad_compromisos_cant']

        self.assertEqual(len(self.indics), jurisdictions)
        self.assertEqual(compromisos, compromisos_actual)

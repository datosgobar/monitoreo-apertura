#! coding: utf-8

import os
import unittest
from indicadores_pad.indicators import PADIndicators


class DocumentationTest(unittest.TestCase):
    """Tests para la clase PADIndicators. Se aprovecha que si se le pasa al
        reader un diccionario de Python en vez de un ID a un spreadsheet, te
        devuelve el mismo diccionario para poder testear solo la funcionalidad
        de cálculo de indicadores.
    Los compromisos reales obtenidos de la panilla de cálculo del PAD no
        tienen rutas a los catálogos .json sino URLs. La librería usada para
        procesarlos debe poder leerlos de ambas fuentes indistintamente.
    """

    SAMPLES_DIR = os.path.join('indicadores_pad', 'tests', 'samples')

    @classmethod
    def setUpClass(cls):
        cls.pad = PADIndicators()

    def test_documentation_indicators_single_valid_dataset(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_title': u'Título del dataset'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_no_documentados_cant': 0,
                'pad_items_documentados_cant': 1,
                'pad_items_documentados_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_documentation_indicators_single_invalid_dataset(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_invalid_dataset.json'),
                            'dataset_title': u'Título del dataset'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_no_documentados_cant': 1,
                'pad_items_documentados_cant': 0,
                'pad_items_documentados_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_documentation_indicators_missing_dataset_in_catalog(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_title': u'Dataset que no está en el .json'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_no_documentados_cant': 1,
                'pad_items_documentados_cant': 0,
                'pad_items_documentados_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_documentation_indicators_one_valid_one_invalid(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'multiple_datasets.json'),
                            'dataset_title': u'Título del dataset'
                        },
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'multiple_datasets.json'),
                            'dataset_title': u'Título del dataset 2'
                        },
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_no_documentados_cant': 1,
                'pad_items_documentados_cant': 0,
                'pad_items_documentados_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_documentation_indicators_several_items(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_title': u'Título del dataset'
                        }
                    ]
                },
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_title': u'Dataset que no está en el .json'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_no_documentados_cant': 1,
                'pad_items_documentados_cant': 1,
                'pad_items_documentados_pct': 50
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_documentation_indicators_several_items_different_catalogs(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_title': u'Título del dataset'
                        }
                    ]
                },
                {
                    'dataset': [
                        {
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_invalid_dataset.json'),
                            'dataset_title': u'Título del dataset'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_no_documentados_cant': 1,
                'pad_items_documentados_cant': 1,
                'pad_items_documentados_pct': 50
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

#! coding: utf-8
import os
import unittest
from indicadores_pad.indicators import PADIndicators, add_dicts


class NetworkIndicators(unittest.TestCase):
    SAMPLES_DIR = os.path.join('tests', 'samples')

    def setUp(self):
        self.pad = PADIndicators()

    def test_network_indicators_single_jurisdiction(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_license': 'licencia válida',
                            'distribution': [
                                {
                                    'distribution_downloadURL':
                                        'http://datos.gob.ar/data.json'
                                }
                            ],
                            'dataset_title': u"Título del dataset",
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'distribution': [
                                {
                                    'distribution_downloadURL': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        indics, network_indics = self.pad.generate_pad_indicators(spreadsheet)

        # Los indicadores en común deben ser exactamente iguales
        self.assertDictContainsSubset(indics['jurisdiccion'], network_indics)

    def test_network_indicators_multiple_jurisdictions(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_license': 'licencia válida',
                            'distribution': [
                                {
                                    'distribution_downloadURL':
                                        'http://datos.gob.ar/data.json'
                                }
                            ],
                            'dataset_title': u"Título del dataset",
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'dataset_license': 'licencia válida',
                            'distribution': [
                                {
                                    'distribution_downloadURL': ''
                                }
                            ]
                        }
                    ]
                }
            ],
            'otra_jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_license': '',
                            'distribution': [
                                {
                                    'distribution_downloadURL':
                                        'http://datos.gob.ar/data.json'
                                }
                            ],
                            'dataset_title': u"Dataset que no está en el .json",
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'distribution': [
                                {
                                    'distribution_downloadURL': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        indics, network_indics = self.pad.generate_pad_indicators(spreadsheet)

        expected = {}
        for jurisdiccion_indics in indics.values():
            for name, value in jurisdiccion_indics.items():
                if type(value) != int:
                    continue

                expected[name] = expected.get(name, 0) + value

        self.assertDictContainsSubset(expected, network_indics)

        self.assertEqual(network_indics['pad_items_documentados_pct'],
                         0)
        self.assertEqual(network_indics['pad_items_licencia_pct'],
                         50)
        self.assertEqual(network_indics['pad_items_actualizados_pct'],
                         50)
        self.assertEqual(network_indics['pad_items_descarga_pct'],
                         0)

#! coding: utf-8
import os
import unittest
from indicadores_pad.indicators import PADIndicators


class UpdatedTest(unittest.TestCase):
    SAMPLES_DIR = os.path.join('tests', 'samples')

    def setUp(self):
        self.pad = PADIndicators()

    def test_compare_single_item(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_actualizados_cant': 1,
                'pad_items_desactualizados_cant': 0,
                'pad_items_actualizados_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_compare_single_item_same_periodicity(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1Y'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_actualizados_cant': 1,
                'pad_items_desactualizados_cant': 0,
                'pad_items_actualizados_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_compare_several_datasets(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1Y'
                        },
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_actualizados_cant': 1,
                'pad_items_desactualizados_cant': 0,
                'pad_items_actualizados_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_compare_several_items(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1Y'
                        }
                    ]
                },
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1Y'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_actualizados_cant': 2,
                'pad_items_desactualizados_cant': 0,
                'pad_items_actualizados_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_compare_item_associated_catalog(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_title': u"Título del dataset",
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_accrualPeriodicity': 'R/P1M'

                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_actualizados_cant': 1,
                'pad_items_desactualizados_cant': 0,
                'pad_items_actualizados_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_item_updated_but_not_in_catalog(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'compromiso_actualizacion': 'R/P1Y',
                    'dataset': [
                        {
                            'dataset_title': u"Dataset que no está en el .json",
                            'catalog_datajson_url':
                                os.path.join(self.SAMPLES_DIR,
                                             'single_valid_dataset.json'),
                            'dataset_accrualPeriodicity': 'R/P1M'

                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_actualizados_cant': 0,
                'pad_items_desactualizados_cant': 1,
                'pad_items_actualizados_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])
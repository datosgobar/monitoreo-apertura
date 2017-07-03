#! coding: utf-8
import os
import unittest
from indicadores_pad.indicators import PADIndicators


class UpdatedTest(unittest.TestCase):
    SAMPLES_DIR = os.path.join('tests', 'samples')

    def setUp(self):
        self.pad = PADIndicators()

    def test_compare_single_item(self):
        spreadsheet = [
            {
                'compromiso_actualizacion': 'R/P1Y',
                'dataset': [
                    {
                        'dataset_accrualPeriodicity': 'R/P1M'
                    }
                ]
            }
        ]

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_actualizados_cant': 1,
            'pad_items_desactualizados_cant': 0,
            'pad_items_actualizados_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_compare_single_item_same_periodicity(self):
        spreadsheet = [
            {
                'compromiso_actualizacion': 'R/P1Y',
                'dataset': [
                    {
                        'dataset_accrualPeriodicity': 'R/P1Y'
                    }
                ]
            }
        ]

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_actualizados_cant': 1,
            'pad_items_desactualizados_cant': 0,
            'pad_items_actualizados_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_compare_several_datasets(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_actualizados_cant': 1,
            'pad_items_desactualizados_cant': 0,
            'pad_items_actualizados_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_compare_several_items(self):
        spreadsheet = [
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
        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_actualizados_cant': 2,
            'pad_items_desactualizados_cant': 0,
            'pad_items_actualizados_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_compare_item_associated_catalog(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_actualizados_cant': 1,
            'pad_items_desactualizados_cant': 0,
            'pad_items_actualizados_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_item_updated_but_not_in_catalog(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_actualizados_cant': 0,
            'pad_items_desactualizados_cant': 1,
            'pad_items_actualizados_pct': 0
        }
        self.assertDictContainsSubset(expected, actual)
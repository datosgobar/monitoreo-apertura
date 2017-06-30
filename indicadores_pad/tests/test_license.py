#! coding: utf-8

import unittest


from indicadores_pad.indicators import PADIndicators


class LicenseTest(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_single_item_licensed(self):
        spreadsheet = [
            {
                'dataset': [
                    {
                        'dataset_license': 'licencia válida'
                    }
                ]
            }
        ]
        actual = self.pad.generate_pad_indicators(spreadsheet)

        expected = {
            'pad_items_licencia_cant': 1,
            'pad_items_sin_licencia_cant': 0,
            'pad_items_licencia_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_single_item_empty_license_field(self):
        spreadsheet = [
            {
                'dataset': [
                    {
                        'dataset_license': ''
                    }
                ]
            }
        ]
        actual = self.pad.generate_pad_indicators(spreadsheet)

        expected = {
            'pad_items_licencia_cant': 0,
            'pad_items_sin_licencia_cant': 1,
            'pad_items_licencia_pct': 0
        }
        self.assertDictContainsSubset(expected, actual)

    def test_single_item_missing_license_field(self):
        spreadsheet = [
            {
                'dataset': [
                    {
                    }
                ]
            }
        ]
        actual = self.pad.generate_pad_indicators(spreadsheet)

        expected = {
            'pad_items_licencia_cant': 0,
            'pad_items_sin_licencia_cant': 1,
            'pad_items_licencia_pct': 0
        }
        self.assertDictContainsSubset(expected, actual)

    def test_several_items(self):
        spreadsheet = [
            {
                'dataset': [
                    {
                        'dataset_license': ''
                    }
                ]
            },
            {
                'dataset': [
                    {
                        'dataset_license': 'licencia válida'
                    }
                ]
            },
            {
                'dataset': [
                    {
                    }
                ]
            }
        ]
        actual = self.pad.generate_pad_indicators(spreadsheet)

        expected = {
            'pad_items_licencia_cant': 1,
            'pad_items_sin_licencia_cant': 2,
            'pad_items_licencia_pct': 33.33
        }
        self.assertDictContainsSubset(expected, actual)
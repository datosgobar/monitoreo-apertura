#! coding: utf-8

import unittest


from indicadores_pad.indicators import PADIndicators


class LicenseTest(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_single_item_licensed(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_license': 'licencia válida'
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_licencia_cant': 1,
                'pad_items_sin_licencia_cant': 0,
                'pad_items_licencia_pct': 100
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_single_item_empty_license_field(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_license': ''
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_licencia_cant': 0,
                'pad_items_sin_licencia_cant': 1,
                'pad_items_licencia_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_single_item_missing_license_field(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_licencia_cant': 0,
                'pad_items_sin_licencia_cant': 1,
                'pad_items_licencia_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_several_items(self):
        spreadsheet = {
            'jurisdiccion': [
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
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_licencia_cant': 1,
                'pad_items_sin_licencia_cant': 2,
                'pad_items_licencia_pct': 33.33
            }
        }

        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_multiple_jurisdictions(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_license': ''
                        }
                    ]
                }
            ],

            'otra_jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_license': 'licencia válida'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)[0]

        expected = {
            'jurisdiccion': {
                'pad_items_licencia_cant': 0,
                'pad_items_sin_licencia_cant': 1,
                'pad_items_licencia_pct': 0
            },
            'otra_jurisdiccion': {
                'pad_items_licencia_cant': 1,
                'pad_items_sin_licencia_cant': 0,
                'pad_items_licencia_pct': 100
            }


        }

        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])
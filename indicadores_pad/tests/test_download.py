#! coding: utf-8
import unittest
from indicadores_pad.indicators import PADIndicators


class DownloadTest(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_download_single_item(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_downloadURL':
                                        'http://datos.gob.ar/data.json'
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_descarga_cant': 1,
                'pad_items_no_descarga_cant': 0,
                'pad_items_descarga_pct': 100
            }
        }

        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_download_invalid_url(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    # TODO: mejor método??
                                    'distribution_downloadURL':
                                        'http://urlcompletamenteinvalida.com'
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_descarga_cant': 0,
                'pad_items_no_descarga_cant': 1,
                'pad_items_descarga_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_download_missing_url(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_descarga_cant': 0,
                'pad_items_no_descarga_cant': 1,
                'pad_items_descarga_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_download_many_datasets(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_downloadURL':
                                        'http://datos.gob.ar/data.json'
                                }
                            ]
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

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_descarga_cant': 0,
                'pad_items_no_descarga_cant': 1,
                'pad_items_descarga_pct': 0
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_download_many_items(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_downloadURL':
                                        'http://datos.gob.ar/data.json'
                                }
                            ]
                        }
                    ]
                },
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_downloadURL': ''
                                }
                            ]
                        }
                    ]
                },
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'jurisdiccion': {
                'pad_items_descarga_cant': 1,
                'pad_items_no_descarga_cant': 1,
                'pad_items_descarga_pct': 50
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

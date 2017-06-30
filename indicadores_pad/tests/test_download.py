#! coding: utf-8
import unittest
from indicadores_pad.indicators import PADIndicators


class DownloadTest(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_download_single_item(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_descarga_cant': 1,
            'pad_items_no_descarga_cant': 0,
            'pad_items_descarga_pct': 100
        }
        self.assertDictContainsSubset(expected, actual)

    def test_download_invalid_url(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_descarga_cant': 0,
            'pad_items_no_descarga_cant': 1,
            'pad_items_descarga_pct': 0
        }
        self.assertDictContainsSubset(expected, actual)

    def test_download_missing_url(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_descarga_cant': 0,
            'pad_items_no_descarga_cant': 1,
            'pad_items_descarga_pct': 0
        }
        self.assertDictContainsSubset(expected, actual)

    def test_download_many_datasets(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_descarga_cant': 0,
            'pad_items_no_descarga_cant': 1,
            'pad_items_descarga_pct': 0
        }
        self.assertDictContainsSubset(expected, actual)

    def test_download_many_items(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_items_descarga_cant': 1,
            'pad_items_no_descarga_cant': 1,
            'pad_items_descarga_pct': 50
        }
        self.assertDictContainsSubset(expected, actual)

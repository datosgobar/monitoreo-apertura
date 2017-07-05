#! coding: utf-8
import unittest
from indicadores_pad.indicators import PADIndicators


class FrequencyIndicator(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_count_one_frecuency(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_datasets_frecuencia_cant': {
                    'R/P1M': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_count_several_from_same_item(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                            'dataset_accrualPeriodicity': 'R/P1Y'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_datasets_frecuencia_cant': {
                    'R/P1M': 4,
                    'R/P1Y': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_count_several_different_items(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        }
                    ]
                },
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        }
                    ]
                },
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        }
                    ]
                },
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1Y'
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_datasets_frecuencia_cant': {
                    'R/P1M': 3,
                    'R/P1Y': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_indicator_ignores_missing_periodicity(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'dataset_accrualPeriodicity': 'R/P1M'
                        },
                        {
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_datasets_frecuencia_cant': {
                    'R/P1M': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])


class FormatIndicator(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_count_one_format(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_format': 'csv'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_distributions_formatos_cant': {
                    'csv': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_count_several_formats_same_item(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_format': 'csv'
                                },
                                {
                                    'distribution_format': 'csv'
                                },
                                {
                                    'distribution_format': 'xlsx'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_distributions_formatos_cant': {
                    'csv': 2,
                    'xlsx': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_several_formats_different_item(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_format': 'csv'
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
                                    'distribution_format': 'csv'
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
                                    'distribution_format': 'xlsx'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_distributions_formatos_cant': {
                    'csv': 2,
                    'xlsx': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])

    def test_indicator_ignores_missing_format(self):
        spreadsheet = {
            'jurisdiccion': [
                {
                    'dataset': [
                        {
                            'distribution': [
                                {
                                    'distribution_format': 'csv'
                                },
                                {
                                    'distribution_format': ''
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        indics = self.pad.generate_pad_indicators(spreadsheet)[0]
        expected = {
            'jurisdiccion': {
                'pad_distributions_formatos_cant': {
                    'csv': 1
                }
            }
        }
        for k, v in expected.items():
            self.assertDictContainsSubset(v, indics[k])
#! coding: utf-8
import unittest
from indicadores_pad.indicators import PADIndicators


class FrequencyIndicator(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_count_one_frecuency(self):
        spreadsheet = [
            {
                'dataset': [
                    {
                        'dataset_accrualPeriodicity': 'R/P1M'
                    }
                ]
            }
        ]

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_datasets_frecuencia_cant': {
                'R/P1M': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

    def test_count_several_from_same_item(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_datasets_frecuencia_cant': {
                'R/P1M': 4,
                'R/P1Y': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

    def test_count_several_different_items(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_datasets_frecuencia_cant': {
                'R/P1M': 3,
                'R/P1Y': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

    def test_indicator_ignores_missing_periodicity(self):
        spreadsheet = [
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

        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_datasets_frecuencia_cant': {
                'R/P1M': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)


class FormatIndicator(unittest.TestCase):

    def setUp(self):
        self.pad = PADIndicators()

    def test_count_one_format(self):
        spreadsheet = [
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
        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_distributions_formatos_cant': {
                'csv': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

    def test_count_several_formats_same_item(self):
        spreadsheet = [
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
        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_distributions_formatos_cant': {
                'csv': 2,
                'xlsx': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

    def test_several_formats_different_item(self):
        spreadsheet = [
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
        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_distributions_formatos_cant': {
                'csv': 2,
                'xlsx': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

    def test_indicator_ignores_missing_format(self):
        spreadsheet = [
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
        actual = self.pad.generate_pad_indicators(spreadsheet)
        expected = {
            'pad_distributions_formatos_cant': {
                'csv': 1
            }
        }
        self.assertDictContainsSubset(expected, actual)

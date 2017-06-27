#! coding: utf-8

import nose
import unittest

from indicadores_pad.indicators import PADIndicators

SPREADSHEET = '1uG68Yq9z1l6IX1kW8A3uO9yGHSNqDglFuagk7BxKOaw'


class IndicatorsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pad = PADIndicators()

    def test_assert_true(self):
        self.assertTrue(True)

    def test_read_sheet(self):
        rows = self.pad.generate_pad_indicators(SPREADSHEET)
        self.assertTrue(rows > 100, "rows menor a 100: {}".format(rows))

if __name__ == '__main__':
    nose.run(defaultTest=__name__)

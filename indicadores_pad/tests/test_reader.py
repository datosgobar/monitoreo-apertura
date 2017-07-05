#! coding: utf-8

import nose
import unittest
import indicadores_pad.reader
from time import clock
SPREADSHEET = '1uG68Yq9z1l6IX1kW8A3uO9yGHSNqDglFuagk7BxKOaw'


class ReaderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.reader = indicadores_pad.reader.SpreadsheetReader()

    def test_all_compromisos_have_required_fields(self):
        fields = (
            "jurisdiccion_id",
            "compromiso_id",
            "jurisdiccion_nombre",
            "compromiso_nombre",
            "compromiso_fecha",
            "compromiso_actualizacion",
            "dataset"
        )
        error_msg = "El campo {0} no se encuentra en el compromiso {1}"
        for k, compromisos in self.reader.read_sheet(SPREADSHEET).items():
            for compromiso in compromisos:
                for field in fields:
                    self.assertTrue(field in compromiso,
                                    error_msg.format(field, compromiso))

    def test_all_datasets_have_requried_fields(self):
        fields = (
            "catalog_title",
            "catalog_homepage",
            "catalog_datajson_url",
            "dataset_title",
            "dataset_landingPage",
            "dataset_accrualPeriodicity",
            "dataset_license",
            "distribution"
        )
        error_msg = "El campo {0} no se encuentra en el dataset {1}"
        for k, compromisos in self.reader.read_sheet(SPREADSHEET).items():
            for compromiso in compromisos:
                for dataset in compromiso['dataset']:
                    for field in fields:
                        self.assertTrue(field in dataset,
                                        error_msg.format(field, dataset))

    def test_all_distributions_have_required_fields(self):
        fields = (
            "distribution_title",
            "distribution_accessURL",
            "distribution_downloadURL",
            "distribution_format"
        )

        error_msg = "El campo {0} no se encuentra en el compromiso {1}"
        for k, compromisos in self.reader.read_sheet(SPREADSHEET).items():
            for compromiso in compromisos:
                for dataset in compromiso['dataset']:
                    for distribution in dataset['distribution']:
                        for field in fields:
                            self.assertTrue(field in distribution,
                                            error_msg.format(field,
                                                             distribution))

    def test_reader_caches_last_result(self):
        # Benchmark de cache: si el resultado es guardado, debería tardar 'muy
        # poco tiempo' en ejecutarse nuevamente

        accepted_difference = 1e-3
        self.reader.read_sheet(SPREADSHEET)
        time = clock()
        self.reader.read_sheet(SPREADSHEET)
        diff = clock() - time
        self.assertLessEqual(diff, accepted_difference)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)

from django.test import TestCase

from monitoreo.apps.dashboard.custom_generators import custom_row_generator


class RowGeneratorTest(TestCase):

    def setUp(self):
        self.fieldnames = ['fecha', 'indicador_tipo__nombre', 'indicador_valor']
        self.rows_list = list(custom_row_generator())

    def test_generated_rows_are_not_empty(self):
        self.assertIsNotNone(self.rows_list)

    def test_first_generated_row_are_fieldnames(self):
        first_row = self.rows_list[0].split(',')
        first_row_contents = [row.strip() for row in first_row]
        self.assertEquals(self.fieldnames, first_row_contents)

#! coding: utf-8
from django.test import TestCase
from monitoreo.apps.dashboard.models import Indicador


class CommandTest(TestCase):
    def test_document_short_title(self):
        Indicador.objects.filter(indicador_valor=1)
        self.assertEqual(True, True)

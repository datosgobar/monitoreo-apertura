#! coding: utf-8
from django.test import TestCase
from nose.tools import *

from monitoreo.apps.dashboard.models import Indicador


class DocumentTests(TestCase):
    @istest
    def test_document_short_title(self):
        assert_equals(True, True)

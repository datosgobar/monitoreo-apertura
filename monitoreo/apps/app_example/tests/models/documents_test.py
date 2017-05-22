# coding=utf-8
from django.test import TestCase
from nose.tools import *

from monitoreo.apps.app_example.models import Document


class DocumentTests(TestCase):
    @istest
    def document_short_title(self):
        document = a_document(title="long title")

        assert_equals("long", document.short_title())


def a_document(title):
    return Document.objects.create(title=title)

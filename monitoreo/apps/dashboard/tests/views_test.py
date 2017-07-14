#! coding: utf-8
from django.test import TestCase, Client
from django.urls import reverse

from monitoreo.apps.dashboard.views import landing, compromisos, red_nodos


class ViewsTest(TestCase):
    def test_landing_with_no_indicators_loaded_returns_500(self):
        response = Client().get(reverse('dashboard:landing'))
        self.assertEqual(response.status_code, 500)

    
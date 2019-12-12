import json

import requests_mock
from django.test import TestCase, Client
from django.urls import reverse

from monitoreo.apps.validator.tests.helpers import open_catalog


class ValidatorTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.validator_url = reverse('validator')
        cls.validator_success_url = reverse('validator_success')

    @requests_mock.mock()
    def test_valid_catalog_redirects_to_success_page(self, mock):
        with open_catalog('sample_data.json') as sample:
            sample_json = json.loads(sample.read().decode('utf-8'))
            mock.head('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            mock.get('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            form_data = {
                'catalog_url': 'https://fakeurl.com/data.json',
                'format': 'json'
            }

            response = self.client.post(self.validator_url, form_data)

            self.assertEqual(response.url, self.validator_success_url)

    @requests_mock.mock()
    def test_invalid_catalog_redirects_to_success_page_with_validation_messages(self, mock):
        with open_catalog('invalid_data.json') as sample:
            sample_json = json.loads(sample.read().decode('utf-8'))
            mock.head('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            mock.get('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            form_data = {
                'catalog_url': 'https://fakeurl.com/data.json',
                'format': 'json'
            }

            response = self.client.post(self.validator_url, form_data, follow=True)
            self.assertEqual(response.context['request'].get_full_path(),
                             self.validator_success_url)

            messages = list(response.context['messages'])
            messages = [message.message for message in messages]
            expected_validation_message = "En dataset Lácteos - Porcentaje de Sólidos en Leche" \
                                          " Cruda: 'porcentaje_grasa_butirosa_kg_solidos_leche_" \
                                          "cruda_nivel_nacional' is not valid under any of the" \
                                          " given schemas"
            self.assertIn(expected_validation_message, messages)

    def test_invalid_url_redirects_to_form(self):
        form_data = {
            'catalog_url': 'this_is_not_a_url',
            'format': 'json'
        }

        response = self.client.post(self.validator_url, form_data)
        self.assertIn('validator.html', response.template_name)

        message = str(list(response.context['messages'])[0])
        self.assertIn("Error descargando el catálogo", message)

    @requests_mock.mock()
    def test_redirects_to_form_if_formats_differ(self, mock):
        with open_catalog('invalid_data.json') as sample:
            sample_json = json.loads(sample.read().decode('utf-8'))
            mock.head('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            mock.get('https://fakeurl.com/data.json', json=sample_json, status_code=200)
            form_data = {
                'catalog_url': 'https://fakeurl.com/data.json',
                'format': 'xlsx'
            }

            response = self.client.post(self.validator_url, form_data)
            self.assertIn('validator.html', response.template_name)

            message = str(list(response.context['messages'])[0])
            self.assertIn("No se pudo parsear el catálogo ingresado", message)

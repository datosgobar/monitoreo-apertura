import logging

import requests
from requests import RequestException, ConnectionError
from django import forms
from django.core.exceptions import ValidationError
from pydatajson import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog

from monitoreo.apps.dashboard.models.tasks import TasksConfig


class ValidatorForm(forms.Form):
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]

    catalog_url = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    format = forms.ChoiceField(choices=FORMAT_CHOICES,
                               widget=forms.Select(attrs={'class': 'format form-control'}))

    def validate_fields(self):
        cleaned_data = self.clean()
        url = cleaned_data.get('catalog_url')
        catalog_format = cleaned_data.get('format')

        base_request_error_message = "Error descargando el catálogo: "
        try:
            response = requests.head(url)
            response.raise_for_status()
        except ConnectionError:
            raise ValidationError(base_request_error_message + "no existe el dominio ingresado")
        except RequestException:
            status_code = requests.head(url).status_code
            raise ValidationError(base_request_error_message + f"status code {status_code}")

        parse_error_message = "No se pudo parsear el catálogo ingresado"
        try:
            DataJson(url, catalog_format=catalog_format)
        except NonParseableCatalog:
            raise ValidationError(parse_error_message)
        except Exception as e:
            logging.getLogger(__file__).error(e)
            raise ValidationError(parse_error_message)

    def validate_catalog(self):
        catalog_url = self.cleaned_data['catalog_url']
        catalog_format = self.cleaned_data['format']
        validate_broken_urls = TasksConfig().get_solo().validation_url_check

        catalog = DataJson(catalog=catalog_url, catalog_format=catalog_format, )

        all_errors = catalog.validate_catalog(only_errors=True, broken_links=validate_broken_urls)
        error_messages = []

        catalog_validation = all_errors['error']['catalog']
        if catalog_validation['errors']:
            error_messages.append(f"En catálogo {catalog_validation['title']}:"
                                  f" {catalog_validation['errors']}")

        for dataset_validation in all_errors['error']['dataset']:
            for error in dataset_validation['errors']:
                error_messages.append(f"En dataset {dataset_validation['title']}:"
                                      f" {error['message']}")

        return error_messages

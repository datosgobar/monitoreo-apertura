import logging

import requests
from requests import RequestException
from django import forms
from django.core.exceptions import ValidationError
from pydatajson import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog


class ValidatorForm(forms.Form):
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]

    catalog_url = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    format = forms.ChoiceField(choices=FORMAT_CHOICES,
                               widget=forms.Select(attrs={'class': 'format form-control'}))

    def validate_fields(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('catalog_url')
        catalog_format = cleaned_data.get('format')

        try:
            requests.head(url).raise_for_status()
        except RequestException:
            raise ValidationError("Error descargando el catálogo")

        parse_error_message = "No se pudo parsear el catálogo ingresado"
        try:
            DataJson(url, catalog_format=catalog_format)
        except NonParseableCatalog:
            raise ValidationError(parse_error_message)
        except Exception as e:
            logging.getLogger(__file__).error(e)
            raise ValidationError(parse_error_message)

    def get_error_messages(self):
        catalog_url = self.cleaned_data['catalog_url']
        catalog_format = self.cleaned_data['format']
        catalog = DataJson(catalog=catalog_url, catalog_format=catalog_format)

        all_errors = catalog.validate_catalog(only_errors=True)
        error_messages = []

        catalog_validation = all_errors['error']['catalog']
        if catalog_validation['errors']:
            error_messages.append("En catálogo {}: {}". format(catalog_validation['title'],
                                                               catalog_validation['errors']))

        for dataset_validation in all_errors['error']['dataset']:
            for error in dataset_validation['errors']:
                error_messages.append("En dataset {}: {}".format(dataset_validation['title'],
                                                                 error['message']))

        return error_messages

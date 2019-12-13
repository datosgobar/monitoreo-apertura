import logging

import requests
from requests.exceptions import MissingSchema, RequestException, ConnectionError
from django.core.exceptions import ValidationError
from pydatajson import DataJson
from pydatajson.custom_exceptions import NonParseableCatalog

from monitoreo.apps.dashboard.models.tasks import TasksConfig


class Validator:

    def __init__(self, catalog_url, catalog_format):
        self.catalog_url = catalog_url
        self.catalog_format = catalog_format

    def validate_fields(self):
        base_request_error_message = "Error descargando el catálogo: "
        try:
            response = requests.head(self.catalog_url)
            response.raise_for_status()
        except MissingSchema:
            raise ValidationError(base_request_error_message + "el url ingresado "
                                                               "no es un url válido")
        except ConnectionError:
            raise ValidationError(base_request_error_message + "no existe el dominio ingresado")
        except RequestException:
            status_code = requests.head(self.catalog_url).status_code
            raise ValidationError(base_request_error_message + f"status code {status_code}")

        parse_error_message = "No se pudo parsear el catálogo ingresado"
        try:
            DataJson(self.catalog_url, catalog_format=self.catalog_format)
        except NonParseableCatalog:
            raise ValidationError(parse_error_message)
        except Exception as e:
            logging.getLogger(__file__).error(e)
            raise ValidationError(parse_error_message)

    def get_catalog_errors(self):
        validate_broken_urls = TasksConfig().get_solo().validation_url_check

        catalog = DataJson(catalog=self.catalog_url, catalog_format=self.catalog_format)

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

from django.contrib import messages
from django.core.exceptions import ValidationError

from django.shortcuts import render
from django.views.generic import FormView

from monitoreo.apps.validator.forms.validator_form import ValidatorForm
from monitoreo.apps.validator.validator import Validator


def validator_success(request):
    return render(request, 'validator_success.html')


class ValidatorView(FormView):
    template_name = "validator.html"
    form_class = ValidatorForm
    success_url = '/validator_success/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return self.form_invalid(form)

        cleaned_data = form.clean()
        catalog_url = cleaned_data.get('catalog_url')
        catalog_format = cleaned_data.get('format')

        validator = Validator(catalog_url, catalog_format)

        try:
            validator.validate_fields()
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        error_messages = validator.get_catalog_errors()
        for error_message in error_messages:
            messages.info(request, error_message)
        return self.form_valid(form)

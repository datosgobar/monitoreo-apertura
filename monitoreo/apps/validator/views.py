from django.contrib import messages
from django.core.exceptions import ValidationError

from django.shortcuts import render
from django.views.generic import FormView

from monitoreo.apps.validator.forms.validator_form import ValidatorForm


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

        try:
            form.validate_fields()
        except ValidationError as e:
            messages.error(request, e)
            return self.form_invalid(form)

        error_messages = form.get_error_messages()
        for error_message in error_messages:
            messages.info(request, error_message)
        return self.form_valid(form)

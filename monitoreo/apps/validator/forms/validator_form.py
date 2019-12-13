from django import forms


class ValidatorForm(forms.Form):
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('xlsx', 'XLSX')
    ]

    catalog_url = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    format = forms.ChoiceField(choices=FORMAT_CHOICES,
                               widget=forms.Select(attrs={'class': 'format form-control'}))

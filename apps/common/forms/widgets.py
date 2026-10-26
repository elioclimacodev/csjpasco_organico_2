from django import forms


class PeruvianDateInput(forms.DateInput):
    '''
    Widget reutilizable para fechas con formato del Perú.
    '''
    format = '%d/%m/%Y'

    def __init__(self, attrs=None):
        default_attrs={
            'class': 'form-control',
            'x-mask': '99/99/9999',
            'placeholder': '10/12/2005',
            'autocomplete': 'off',
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(
            attrs=default_attrs,
            format=self.format
        )

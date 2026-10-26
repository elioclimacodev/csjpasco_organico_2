from django import forms

from apps.common.forms import BaseListFiltersForm

from apps.organizacion.models import OrganoJurisdiccional


class OrganoJurisdiccionalForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Órgano Jurisdiccional',
        required=True,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Juzgado de Paz Letrado',
                'autocomplete': 'off',
            }
        )
    )
    siglas = forms.CharField(
        label='Siglas',
        required=False,
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. JPL',
                'autocomplete': 'off',
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            }
        )
    )
    class Meta:
        model = OrganoJurisdiccional
        fields = ['nombre', 'siglas',]


class OrganoJurisdiccionalFiltersForm(BaseListFiltersForm):
    '''
    Este formulario actualmente no requiere filtros adicionales.
    '''
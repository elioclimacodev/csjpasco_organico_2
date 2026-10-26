from django import forms

from apps.common.forms import BaseListFiltersForm

from apps.organizacion.models import MateriaJurisdiccional


class MateriaJurisdiccionalForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Materia',
        required=True,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Laboral',
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
                'placeholder': 'Ejem. LA',
                'autocomplete': 'off',
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            }
        )
    )
    class Meta:
        model = MateriaJurisdiccional
        fields = ['nombre', 'siglas',]


class MateriaJurisdiccionalFiltersForm(BaseListFiltersForm):
    '''
    '''
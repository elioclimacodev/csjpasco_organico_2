from django import forms

from apps.organizacion.models.distrito_judicial import DistritoJudicial
from apps.common.forms import BaseListFiltersForm


class DistritoJudicialForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Distrito Judicial',
        required=True,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Pasco',
            }
        )
    )

    corte = forms.CharField(
        label='Corte',
        required=True,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Corte Superior de Justicia de Pasco',
            }
        )
    )
  
    siglas = forms.CharField(
        label='Siglas',
        required=True,
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. CSJPA',
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            }
        )
    )
    # latitud = forms.CharField(
    #     label='Latitud',
    #     required=False,
    #     max_length=15,
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Ejem. -10.692306',
    #         }
    #     )        
    # )
    # longitud = forms.CharField(
    #     label='Longitud',
    #     required=False,
    #     max_length=15,
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Ejem. --76.259542',
    #         }
    #     )        
    # )
    class Meta:
        model = DistritoJudicial
        fields = [
            'nombre', 'corte', 'siglas',
            # 'latitud', 'longitud',
        ]


class DistritoJudicialFiltersForm(BaseListFiltersForm):
    '''
    Este formulario actualmente no requiere de filtros adicionales.
    '''

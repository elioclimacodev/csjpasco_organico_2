from django import forms

from apps.common.forms import BaseListFiltersForm
from apps.ubicaciones.models import Distrito


class DistritoForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Provincia',
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Simón Bolívar',
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            }
        )
    )

    ubigeo_inei = forms.CharField(
        label='Ubigeo INEI',
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. 190109',
                'x-mask': '999999',
            }
        )
    )

    ubigeo_reniec = forms.CharField(
        label='Ubigeo RENIEC',
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. 180110',
                'x-mask': '999999',
            }
        )
    )

    codigo_postal = forms.CharField(
        label='Código postal',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. 19002',
                'x-mask': '99999',
            }
        )
    )
    
    class Meta:
        model = Distrito
        fields = [
            'nombre',
            'ubigeo_inei', 'ubigeo_reniec', 'codigo_postal',
        ]    
        
    
class DistritoFiltersForm(BaseListFiltersForm):
    pass
from django import forms

from apps.common.forms import BaseListFiltersForm

from apps.ubicaciones.models import Pais


class CountryForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Nombre',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Perú',
                'x-on:input': (
                    "$el.value = $el.value"
                    ".replace(/[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\\s]/g, '')" # Elimina caracteres no alfabéticos.
                    ".replace(/\\s{2,}/g, ' ')" # Mantiene un solo espacio y elimina si hay más.
                    ".replace(/^\\s+/, '')"
                    ".toUpperCase()"
                ),
                'x-on:paste': (
                    "$event.preventDefault();"
                    "let text = $event.clipboardData.getData('text');"
                    "let clean = text.replace(/[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\\s]/g, '').toUpperCase();"
                    "$el.value = clean;"
                    "$el.dispatchEvent(new Event('input'));"
                ),                
                'x-on:blur': '$el.value = $el.value.trimEnd()',
            }
        )
    )
    
    codigo_alpha2 = forms.CharField(
        label='Código Alpha-2',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. PE',
                'maxlength': '2',
                'x-mask': 'aa', 
                'x-on:input': '$el.value = $el.value.toUpperCase()'
            }
        )
    )
    
    codigo_alpha3 = forms.CharField(
        label='Código Alpha-3',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. PER',
                'maxlength': '3',
                'x-mask': 'aaa',
                'x-on:input': '$el.value = $el.value.toUpperCase()'
            }
        )
    )
    codigo_numerico = forms.CharField(
        label='Código numérico',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. 604',
                'x-mask': '999',
            }
        )
    )
    codigo_internacional = forms.CharField(
        label='Código internacional',
        required=False,
        help_text='Debe incluir el signo +',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. +51',
                'x-mask': '+999999',
            }
        )
    )    
    
    class Meta:
        model = Pais
        fields = [
            'nombre',
            'codigo_alpha2', 'codigo_alpha3',
            'codigo_numerico', 'codigo_internacional'
        ]
        
        
class CountryFiltersForm(BaseListFiltersForm):
    pass
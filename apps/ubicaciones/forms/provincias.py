from django import forms

from apps.ubicaciones.models import Provincia

from apps.common.forms import BaseListFiltersForm


class ProvinciaForm(forms.ModelForm):
    nombre = forms.CharField(
        label='Región',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Pasco',
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
    ubigeo_inei = forms.CharField(
        label='Ubigeo INEI',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. 19',
                'x-mask': '999999',
            }
        )
    )
    ubigeo_reniec = forms.CharField(
        label='Ubigeo RENIEC',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. 19',
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
                'placeholder': 'Ejem. 19001',
                'x-mask': '99999',
            }
        )
    )
    
    class Meta:
        model = Provincia
        fields = ['nombre', 'ubigeo_inei', 'ubigeo_reniec', 'codigo_postal',]
        
    
class ProvinciaFiltersForm(BaseListFiltersForm):
    pass
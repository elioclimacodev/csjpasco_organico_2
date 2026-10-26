from django import forms

from apps.common.forms import BaseListFiltersForm, PeruvianDateInput

from apps.organizacion.models import DistritoJudicial, CorteJusticia


class CorteJusticiaForm(forms.ModelForm):
    nivel = forms.ChoiceField(
        label='Nivel',
        required=True,
        choices=CorteJusticia.NivelCorte.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        ),
        error_messages={
            'required': 'Debe seleccionar el nivel de la Corte.'
        }
    )
    nombre = forms.CharField(
        label='Nombre',
        required=True,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Pasco',
                'x-on:input': '$el.value = $el.value.toUpperCase()'
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
                'placeholder': 'Ejem. CSJPA',
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            }
        )
    )

    # fecha_instalacion = forms.DateField(
    #     label='Fecha de instalación',
    #     required=False,
    #     input_formats=['%d/%m/%Y'],
    #     widget=PeruvianDateInput(),
    #     error_messages={
    #         'invalid': 'Ingrese una fecha válida en formato dd/mm/aaaa.',
    #     },
    # )

    # norma_instalacion = forms.CharField(
    #     label='Documento de instalación',
    #     required=False,
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Resolución Administrativa N° 000120-2002-CSJPA-PJ',
    #         }
    #     )
    # )

    # archivo_instalacion = forms.FileField(
    #     label='Archivo de instalación',
    #     required=False,
    #     widget=forms.ClearableFileInput(
    #         attrs={
    #             'class': 'form-control',
    #             'accept': '.pdf',
    #         }
    #     )
    # )
    
    # fecha_funcionamiento = forms.DateField(
    #     label='Fecha de funcionamiento',
    #     required=False,
    #     input_formats=['%d/%m/%Y'],
    #     widget=PeruvianDateInput(),
    #     error_messages={
    #         'invalid': 'Ingrese una fecha válida en formato dd/mm/aaaa.',
    #     },
    # )

    # norma_funcionamiento = forms.CharField(
    #     label='Documento de funcionamiento',
    #     required=False,
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'form-control',
    #             'placeholder': 'Resolución Administrativa N° 000120-2002-CSJPA-PJ',
    #         }
    #     )
    # )

    # archivo_funcionamiento = forms.FileField(
    #     label='Archivo de funcionamiento',
    #     required=False,
    #     widget=forms.ClearableFileInput(
    #         attrs={
    #             'class': 'form-control',
    #             'accept': '.pdf',
    #         }
    #     )
    # )

    class Meta:
        model = CorteJusticia
        fields = [
            'nivel',
            'nombre', 'siglas',
            # 'fecha_instalacion', 'norma_instalacion', 'archivo_instalacion',
            # 'fecha_funcionamiento', 'norma_funcionamiento', 'archivo_funcionamiento',
        ]


class CorteJusticiaFiltersForm(BaseListFiltersForm):
    '''
    Este formulario actualmente no requiere filtros adicionales.
    '''

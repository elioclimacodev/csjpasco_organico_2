from django import forms

from apps.common.forms import BaseListFiltersForm
from apps.common.forms.fields import TreeModelChoiceField

from apps.organizacion.models import SedeJudicial


class SedeJudicialForm(forms.ModelForm):
    sede_superior = TreeModelChoiceField(
        queryset=SedeJudicial.objects.none(), # Ya no necesitas .none() inicial
        parent_field='sede_superior',
        required=False,
        empty_label='--------',
        indent_char='··· ',      # Personalizable: puedes usar '—', '   ', etc.
        indent_factor=1,         # Multiplicador del patrón
        order_by='nombre',       # Campo por el cual ordenar los hermanos
        widget=forms.Select(attrs={
            'class': 'form-control', # Soporta nativamente clases de bootstrap
        })
    )

    nombre = forms.CharField(
        label='Nombre de la Sede',
        required=True,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejem. Subsede Yanahuanca',
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
                'placeholder': 'Ejem. YHCA',
                'autocomplete': 'off',
                'x-on:input': '$el.value = $el.value.toUpperCase()',
            }
        )
    )

    class Meta:
        model = SedeJudicial
        fields = ['sede_superior', 'nombre', 'siglas']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Seteamos la instancia en el field para que sepa a quién excluir en la edición
        self.fields['sede_superior'].instance = self.instance
        self.fields['sede_superior'].queryset = SedeJudicial.objects.all()

    def clean_sede_superior(self):
        # Nota: Corregido el nombre del método (antes tenías clean_parent)
        sede_superior = self.cleaned_data.get('sede_superior')

        if (
            sede_superior
            and self.instance.pk
            and sede_superior.pk == self.instance.pk
        ):
            raise forms.ValidationError(
                'Esta sede no puede ser inmediato superior de sí misma.'
            )

        return sede_superior


class SedeJudicialFiltersForm(BaseListFiltersForm):
    '''
    Este formulario actualmente no requiere de filtros adicionales.
    '''
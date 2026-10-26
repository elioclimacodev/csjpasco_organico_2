from django import forms

from apps.common.forms import BaseListFiltersForm
from .models import Persona


class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = [
            'tipo_documento', 'numero_documento',
            'nombres', 'apellido_paterno', 'apellido_materno',
            'genero', 'fecha_nacimiento', 'estado_civil',
        ]
        widgets = {
            'tipo_documento': forms.Select(
                attrs={
                    'class': 'form-select',
                }),
            'numero_documento': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'nombres': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'apellido_paterno': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'apellido_materno': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'genero': forms.Select(
                attrs={
                    'class': 'form-select',
                }),
            'fecha_nacimiento': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }),
            'estado_civil': forms.Select(
                attrs={
                    'class': 'form-select',
                }),                
        }


class PersonaFiltersForm(BaseListFiltersForm):
    pass

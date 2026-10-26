from django import forms


class BaseListFiltersForm(forms.Form):
    '''
    Formulario base para los listados de los módulos del sistema.
    Incluye:
    - Búsqueda textual.
    - Filtro por estado.
    - Contidad de registros por página.
    - Ordenamiento.

    Para el uso con otros filtros adicionales revisar
    '''
    per_page = forms.IntegerField(
        label='Registros por página',
        required=False,
        initial=10,
        min_value=1,
        max_value=100,
        widget=forms.TextInput(
            attrs={
                'x-mask': '999',
                'class': 'form-control text-center',
                'placeholder': '10',
                'inputmode': 'numeric',
                'style': 'width: 3.5rem;',
            }
        )
    )
    
    search = forms.CharField(
        label='Buscar',
        required=False,
        max_length=256,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Buscar',
                'autocomplete': 'off',
            }
        )
    )

    status = forms.ChoiceField(
        label='Estado',
        required=False,
        choices=[
            ('', 'Estado'),
            ('0', 'Inactivo'),
            ('1', 'Activo'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select',
            }
        )
    )
    order_by = forms.CharField(
        required=False,
        # initial=default_order_by,
        widget=forms.HiddenInput()
    )
    direction = forms.CharField(
        required=False,
        # initial=default_direction ,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, request_path=None, **kwargs):
        '''
        Configura HTMX automáticamente al instanciar el formulario.
        '''
        super().__init__(*args, request_path, **kwargs)

        # self.fields['order_by'].initial = self.default_order_by
        # self.fields['direction'].initial = self.default_direction

        if request_path:
            self.setup_htmx(request_path)

    def setup_htmx(self, request_path):
        '''
        Configura los atributos HTMX de los controles que generan
        actualización automática del listado.
        '''
        common_attrs = {
            'hx-get': request_path,
            'hx-target': '#datatable',
            'hx-swap': 'outerHTML',
            'hx-push-url': 'true',
            'hx-include': '#filters_form',
            'hx-vals': '{"page": 1}',
        }

        self.fields['per_page'].widget.attrs.update({
            **common_attrs,
            'hx-trigger': 'keyup changed delay:300ms',
        })

        self.fields['search'].widget.attrs.update({
            **common_attrs,
            'hx-trigger': 'keyup changed delay:300ms',
            'x-model': 'search',
            'x-ref': 'search_input',
        })

        self.fields['status'].widget.attrs.update({
            **common_attrs,
            'hx-trigger': 'change',
        })

    def clean_per_page(self):
        '''
        Establece el valor por defecto en el campo 'per_page'.
        '''
        value = self.cleaned_data.get('per_page')
        
        if not value:
            return 10
        return min(value, 100)

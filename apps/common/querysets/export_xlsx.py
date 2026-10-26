import io
import xlsxwriter

from django.http import HttpResponse


def get_institutional_formats(workbook):
    '''
    Genera y devuelve un diccionario con los estilos institucionales
    para la exportación del queryset a formato xlsx.
    '''
    color_primary   = '#A00000'
    color_white     = '#FFFFFF'
    color_accent    = '#ABD0BC'
    color_border    = '#590000'

    return {
        'header': workbook.add_format({
            'bold': True, 'font_name': 'Arial', 'font_size': 11,
            'bg_color': color_primary, 'font_color': color_white,
            'border': 1, 'border_color': color_border,
            'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bottom': 2,
        }),
        'cell': workbook.add_format({
            'font_name': 'Arial', 'font_size': 10,
            'border': 1, 'border_color': color_primary,
            'align': 'left', 'valign': 'vcenter', 'text_wrap': False,
        }),
        'cell_center': workbook.add_format({
            'font_name': 'Arial', 'font_size': 10,
            'border': 1, 'border_color': color_primary,
            'align': 'center', 'valign': 'vcenter',
        }),
        'active': workbook.add_format({
            'font_name': 'Arial', 'font_size': 10, 'bold': True,
            'bg_color': color_accent, 'font_color': '#1F3A2F',
            'border': 1, 'border_color': color_primary,
            'align': 'center', 'valign': 'vcenter',
        }),
        'inactive': workbook.add_format({
            'font_name': 'Arial', 'font_size': 10, 'bold': True,
            'bg_color': '#F0E6E6', 'font_color': '#8B0000',
            'border': 1, 'border_color': color_primary,
            'align': 'center', 'valign': 'vcenter',
        }),
    }


def export_queryset_to_xlsx(queryset, columns_config, filename, sheet_name='Datos'):
    """
    Función genérica para exportar cualquier queryset a XLSX.
    
    :param queryset: Queryset de Django ya filtrado y ordenado.
    :param columns_config: Lista de diccionarios definiendo las columnas.
                           Ej: [{'header': 'Nombre', 'field': 'nombre', 'width': 30, 'format': 'cell'}]
    :param filename: Nombre del archivo (sin .xlsx).
    :param sheet_name: Nombre de la pestaña.
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet(sheet_name)
    formats = get_institutional_formats(workbook)

    # 1. Escribir encabezados y ajustar anchos
    for col, config in enumerate(columns_config):
        worksheet.write(0, col, config['header'], formats['header'])
        worksheet.set_column(col, col, config.get('width', 15)) # Ancho por defecto 15 si no se especifica

    # 2. Escribir datos
    for row, obj in enumerate(queryset.iterator(), start=1):
        for col, config in enumerate(columns_config):
            field = config['field']
            format_type = config.get('format', 'cell')
            
            # Obtener el valor (soporta atributos y métodos del modelo)
            value = getattr(obj, field)
            if callable(value):
                value = value()

            # Manejar booleanos con formato especial
            if format_type == 'boolean':
                text = 'Activo' if value else 'Inactivo'
                fmt = formats['active'] if value else formats['inactive']
                worksheet.write(row, col, text, fmt)
            else:
                fmt = formats.get(format_type, formats['cell'])
                worksheet.write(row, col, value, fmt)

    workbook.close()
    output.seek(0)

    # 3. Crear respuesta HTTP
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    return response


# ── Otros usos ───────────────────

# def empleados_export(request):
#     queryset = Empleado.objects.all()
#     # ... (tus filtros y ordenamientos específicos) ...

#     columns = [
#         {'header': 'Nombre Completo', 'field': 'get_full_name', 'width': 40}, # ¡Soporta métodos!
#         {'header': 'Legajo', 'field': 'legajo', 'width': 15, 'format': 'cell_center'},
#         {'header': 'Departamento', 'field': 'departamento__nombre', 'width': 25}, # ¡Soporta lookups!
#         {'header': 'Estado', 'field': 'es_activo', 'width': 15, 'format': 'boolean'},
#     ]

#     return export_queryset_to_xlsx(
#         queryset=queryset,
#         columns_config=columns,
#         filename="Empleados",
#         sheet_name="Empleados"
#     )
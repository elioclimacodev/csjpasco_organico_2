from django.core.validators import FileExtensionValidator


pdf_file_validator = FileExtensionValidator(
    allowed_extensions=['pdf'],
    message='Solo se permiten archivos PDF.'
)
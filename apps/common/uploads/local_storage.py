from pathlib import Path
from uuid import uuid4

from django.utils.deconstruct import deconstructible


@deconstructible
class LocalUploadPath:
    """
    Genera rutas de almacenamiento para archivos de medios.

    Formato:
        <app>/<model>/<tipo>/<uuid>.<extension>

    Compatible con el sistema de migraciones de Django.
    """

    def __init__(
        self,
        app_name,
        model_name,
        document_type,
    ):
        self.app_name = app_name
        self.model_name = model_name
        self.document_type = document_type

    def __call__(self, instance, filename):
        extension = Path(filename).suffix.lower()

        return (
            f'{self.app_name}/'
            f'{self.model_name}/'
            f'{self.document_type}/'
            f'{uuid4()}{extension}'
        )
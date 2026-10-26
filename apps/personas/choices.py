from django.db import models


class TipoDocumento(models.TextChoices):
    DNI = ('DNI', 'Documento Nacional de Identidad')            # 8 dígitos.
    PAS = ('PAS', 'Pasaporte')                                  # 9 a 12 caracteres alfanuméricos.
    CFP = ('CFP', 'Carné de Fuerzas Policiales')                # 8 dígitos.
    CFA = ('CFA', 'Carné de Fuerzas Armadas')                   # 8 dígitos.
    CEX = ('CEX', 'Carné de Extranjería')                       # 1 letra seguida de 8 dígitos, Ejemplo: E12345678.
    CPP = ('CPP', 'Carné de Permiso Temporal de Permanencia')   # 9 dígitos.

class Genero(models.TextChoices):
    MAS = ('MAS', 'Masculino')
    FEM = ('FEM', 'Femenino')

class EstadoCivil(models.TextChoices):
    SOL = ('SOL', 'Soltero')
    CAS = ('CAS', 'Casado')
    DIV = ('DIV', 'Divorciado')
    VDO = ('VDO', 'Viudo')
    UDH = ('UDH', 'Unión de hecho')

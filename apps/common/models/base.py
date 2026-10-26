from django.db import models


class SingletonModel(models.Model):
    '''
    Modelo base para entidades que deben tener un único registro.
    '''
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
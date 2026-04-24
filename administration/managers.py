from django.db import models


class SingletonManager(models.Manager):
    """Manager que apoya el patrón Singleton para Company."""

    def get_solo(self):
        instance = self.first()
        if instance is None:
            raise self.model.DoesNotExist(
                'Aún no se ha registrado la empresa.'
            )
        return instance

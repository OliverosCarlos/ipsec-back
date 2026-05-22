from django.db import models

from core.models import BaseModel


class ExternalNoteTemplate(BaseModel):
    """
    Plantilla de nota externa para cotizaciones.
    El campo `template` almacena contenido HTML (texto enriquecido).
    """

    code = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text='Código único de la plantilla (ej. NOTE-001)',
    )
    name = models.CharField(
        max_length=150,
        help_text='Nombre descriptivo de la plantilla',
    )
    template = models.TextField(
        help_text='Contenido HTML de la nota externa (texto enriquecido)',
    )

    class Meta:
        verbose_name = 'Plantilla de nota externa'
        verbose_name_plural = 'Plantillas de notas externas'
        ordering = ['code']

    def __str__(self):
        return f'[{self.code}] {self.name}'

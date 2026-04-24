from django.db import models

from core.models import BaseModel
from entities.models.catalogs import JobPosition, PersonTitle
from .company import Company


class CompanyContact(BaseModel):
    """Contactos internos de la empresa (representante legal, ventas, soporte…)."""

    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'No especificado'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='contacts',
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    phone_landline = models.CharField(max_length=30, blank=True)
    phone_landline_ext = models.CharField(max_length=10, blank=True)

    job_position = models.ForeignKey(
        JobPosition, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='company_contacts',
    )
    person_title = models.ForeignKey(
        PersonTitle, null=True, blank=True, on_delete=models.PROTECT,
        related_name='company_contacts',
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, default='N')
    photo = models.ImageField(upload_to='company/contacts/', null=True, blank=True)

    is_primary = models.BooleanField(
        default=False, help_text='Contacto principal de la empresa',
    )

    class Meta:
        indexes = [models.Index(fields=['company', 'email'])]
        verbose_name = 'Contacto de Empresa'
        verbose_name_plural = 'Contactos de Empresa'

    def __str__(self) -> str:
        return f'{self.name} ({self.company.legal_name})'

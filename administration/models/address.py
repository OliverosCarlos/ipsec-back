from django.db import models

from core.models import BaseModel
from entities.models.catalogs import Country
from .company import Company


class CompanyAddress(BaseModel):
    """Direcciones de la empresa (fiscal, sucursales, envío, etc.)."""

    KIND_CHOICES = [
        ('FISCAL',   'Fiscal'),
        ('BRANCH',   'Sucursal'),
        ('SHIPPING', 'Envío'),
        ('OTHER',    'Otra'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='addresses',
    )
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='FISCAL')
    name = models.CharField(
        max_length=120, blank=True,
        help_text='Etiqueta de la dirección (ej. "Oficina CDMX")',
    )

    street = models.CharField(max_length=255, blank=True)
    ext_no = models.CharField(max_length=50, blank=True)
    int_no = models.CharField(max_length=50, blank=True)
    neighborhood = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=10)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT,
        related_name='company_addresses', default='MEX',
    )

    is_primary = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['company', 'kind'])]
        verbose_name = 'Dirección de Empresa'
        verbose_name_plural = 'Direcciones de Empresa'

    def __str__(self) -> str:
        label = self.name or self.company.legal_name
        return f'[{self.kind}] {label} - CP {self.zip_code}'

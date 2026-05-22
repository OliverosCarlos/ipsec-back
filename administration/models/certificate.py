from django.db import models

from core.models import BaseModel
from .company import Company


class CompanyCertificate(BaseModel):
    """
    Certificado de Sello Digital (CSD) para timbrado CFDI.

    NOTA DE SEGURIDAD:
    - El archivo .key y la contraseña son sensibles.
    - Se recomienda almacenar los archivos fuera del MEDIA público
      y cifrar `password` en reposo (django-cryptography / django-fernet-fields).
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='certificates',
    )
    serial_number = models.CharField(
        max_length=40, db_index=True,
        help_text='Número de serie del certificado (NoCertificado en CFDI)',
    )
    cer_file = models.FileField(
        upload_to='company/csd/cer/',
        help_text='Archivo .cer del SAT',
    )
    key_file = models.FileField(
        upload_to='company/csd/key/',
        help_text='Archivo .key del SAT',
    )
    password = models.CharField(
        max_length=255,
        help_text='Contraseña del CSD (debe almacenarse cifrada)',
    )

    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Certificado CSD'
        verbose_name_plural = 'Certificados CSD'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'serial_number'],
                name='uniq_company_csd_serial',
            ),
        ]

    def __str__(self) -> str:
        return f'CSD {self.serial_number} - {self.company.legal_name}'

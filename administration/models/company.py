from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from core.models import BaseModel
from entities.models.catalogs import CompanySector, Country
from invoicing.models.sat import SatCatalog
from administration.managers import SingletonManager

# Validación RFC (CFDI 4.0)
RFC_REGEX = r"^([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})$"
# Validación HEX color (#RGB o #RRGGBB)
HEX_COLOR_REGEX = r"^#(?:[0-9a-fA-F]{3}){1,2}$"


class Company(BaseModel):
    """
    Datos de la empresa propietaria del sistema (emisor de CFDI).

    Cumple con CFDI 4.0: RFC, razón social, régimen fiscal y CP fiscal.
    Diseñado como SINGLETON: solo debe existir una instancia.
    """

    PERSON_TYPE = [
        ('FISICA', 'Persona física'),
        ('MORAL',  'Persona moral'),
    ]

    # ── Identificación fiscal (CFDI 4.0) ───────────────────────
    rfc = models.CharField(
        max_length=13,
        unique=True,
        db_index=True,
        validators=[RegexValidator(RFC_REGEX, message='RFC inválido')],
        help_text='RFC del emisor (CFDI 4.0)',
    )
    legal_name = models.CharField(
        max_length=255,
        help_text='Nombre/Razón social EXACTO como en la CSF (CFDI 4.0)',
    )
    person_type = models.CharField(max_length=6, choices=PERSON_TYPE)

    tax_regime = models.ForeignKey(
        SatCatalog,
        on_delete=models.PROTECT,
        related_name='companies_regimen',
        limit_choices_to={'catalog': 'c_RegimenFiscal'},
        help_text='Régimen fiscal del emisor (CFDI 4.0)',
    )
    tax_zip = models.CharField(
        max_length=10,
        help_text='Código postal del domicilio fiscal (CFDI 4.0)',
    )

    # ── Clasificación ─────────────────────────────────────────
    company_sector = models.ForeignKey(
        CompanySector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies',
    )

    # ── Datos comerciales / contacto ──────────────────────────
    commercial_name = models.CharField(max_length=255, blank=True)
    email_billing = models.EmailField(blank=True)
    email_contact = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='companies',
        default='MEX',
    )

    # ── Branding (para PDFs / reportes) ───────────────────────
    logo = models.ImageField(upload_to='company/logos/', null=True, blank=True)
    logo_dark = models.ImageField(
        upload_to='company/logos/',
        null=True,
        blank=True,
        help_text='Variante para fondos oscuros',
    )
    slogan = models.CharField(max_length=255, blank=True)
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        validators=[RegexValidator(HEX_COLOR_REGEX, 'Color HEX inválido (#RRGGBB)')],
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        validators=[RegexValidator(HEX_COLOR_REGEX, 'Color HEX inválido (#RRGGBB)')],
    )

    # ── Datos legales adicionales ─────────────────────────────
    legal_representative = models.CharField(max_length=255, blank=True)

    objects = SingletonManager()

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresa'
        constraints = [
            models.UniqueConstraint(
                fields=['rfc'], name='uniq_company_rfc',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.legal_name} ({self.rfc})'

    def clean(self):
        """Valida singleton + mínimos CFDI 4.0."""
        qs = Company.objects.exclude(pk=self.pk) if self.pk else Company.objects.all()
        if qs.exists():
            raise ValidationError(
                'Solo puede existir una Empresa registrada en el sistema.'
            )

        missing = []
        if not self.legal_name:
            missing.append('legal_name')
        if not self.tax_regime_id:
            missing.append('tax_regime')
        if not self.tax_zip:
            missing.append('tax_zip')
        if missing:
            raise ValidationError({
                '__all__': f'Campos obligatorios CFDI 4.0 faltantes: {", ".join(missing)}',
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

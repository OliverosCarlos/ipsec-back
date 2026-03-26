from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from entities.models.catalogs import CompanySector, Country, JobPosition, PersonTitle
from invoicing.models.sat import SatCatalog

# Validación básica de RFC (personas físicas y morales)
RFC_REGEX = r"^([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})$"


class Partner(models.Model):
    """
    Entidad fiscal (empresa o persona física) que puede tener múltiples roles:
    cliente, proveedor, transportista, etc.
    Debe contener los datos requeridos por CFDI 4.0: RFC, nombre/razón social,
    régimen fiscal (c_RegimenFiscal) y CP del domicilio fiscal (tax_zip).
    """

    PERSON_TYPE = [
        ('FISICA', 'Persona física'),
        ('MORAL',  'Persona moral'),
    ]

    SECTOR_CHOICES = [
        ('PRIVATE', 'Privado'),
        ('PUBLIC',  'Público'),
    ]

    # Identificación fiscal (CFDI 4.0)
    rfc = models.CharField(
        max_length=13,
        unique=True,
        db_index=True,
        validators=[RegexValidator(RFC_REGEX, message="RFC inválido")]
    )
    legal_name = models.CharField(
        max_length=255,
        help_text="Nombre/Razón social EXACTO como en la CSF (CFDI 4.0)"
    )
    person_type = models.CharField(max_length=6, choices=PERSON_TYPE)

    # Régimen fiscal (c_RegimenFiscal) - requerido en CFDI 4.0
    tax_regime = models.ForeignKey(
        SatCatalog,
        on_delete=models.PROTECT,
        related_name="partners_regimen",
        limit_choices_to={'catalog': 'c_RegimenFiscal'},
        help_text="Régimen fiscal del contribuyente (CFDI 4.0)"
    )

    # Código postal del domicilio fiscal (requerido CFDI 4.0 para emisor/receptor)
    tax_zip = models.CharField(
        max_length=10,
        help_text="Código postal del domicilio fiscal (CFDI 4.0)"
    )

    # Clasificación
    sector = models.CharField(
        max_length=10,
        choices=SECTOR_CHOICES,
        blank=True,
        default='',
        help_text="Sector del partner: Privado o Público",
    )
    company_sector = models.ForeignKey(
        CompanySector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partners',
        help_text="Sector/giro de la empresa (Tecnología, Educación, etc.)",
    )

    # Datos comerciales / contacto
    commercial_name = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='partners/logos/', null=True, blank=True)
    email_billing = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    # País del partner; por defecto MEX
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='partners',
        default='MEX'
    )

    # Operación
    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['rfc']),
            models.Index(fields=['active']),
        ]
        verbose_name = "Partner (Entidad)"
        verbose_name_plural = "Partners (Entidades)"

    def clean(self):
        """
        Valida mínimos CFDI 4.0 en la entidad.
        """
        missing = []
        if not self.legal_name:
            missing.append("legal_name")
        if not self.tax_regime_id:
            missing.append("tax_regime")
        if not self.tax_zip:
            missing.append("tax_zip")
        if missing:
            raise ValidationError({
                "__all__": f"Campos obligatorios para CFDI 4.0 faltantes: {', '.join(missing)}"
            })

    def __str__(self) -> str:
        return f"{self.legal_name} ({self.rfc})"

    # Atajos de lectura
    @property
    def is_customer(self) -> bool:
        return self.roles.filter(role='CUSTOMER').exists()

    @property
    def is_supplier(self) -> bool:
        return self.roles.filter(role='SUPPLIER').exists()


class PartnerRole(models.Model):
    """
    Roles asignados al Partner (cliente, proveedor, transportista…).
    Campos específicos por rol (p.ej. DIOT para proveedores).
    """
    ROLE_CHOICES = [
        ('CUSTOMER', 'Cliente'),
        ('SUPPLIER', 'Proveedor'),
        ('CARRIER',  'Transportista'),
        ('OTHER',    'Otro'),
    ]

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # --- Campos específicos por rol ---

    # Requerimientos DIOT (proveedores)
    diot_third_type = models.ForeignKey(
        SatCatalog, null=True, blank=True, on_delete=models.PROTECT,
        related_name='partnerrole_diot_tercero',
        limit_choices_to={'catalog': 'DIOT_TipoTercero'},
        help_text="DIOT: tipo de tercero (04 Nacional, 05 Extranjero, 15 Global). Solo proveedores."
    )
    diot_operation_type = models.ForeignKey(
        SatCatalog, null=True, blank=True, on_delete=models.PROTECT,
        related_name='partnerrole_diot_operacion',
        limit_choices_to={'catalog': 'DIOT_TipoOperacion'},
        help_text="DIOT: tipo de operación (02, 03, 06, 85, 87…). Solo proveedores."
    )

    # Política comercial por rol (opcional)
    default_currency = models.ForeignKey(
        SatCatalog, on_delete=models.PROTECT, null=True, blank=True,
        related_name='partnerrole_currency',
        limit_choices_to={'catalog': 'c_Moneda'}
    )
    payment_terms_days = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('partner', 'role')]
        verbose_name = "Rol de Partner"
        verbose_name_plural = "Roles de Partner"

    def clean(self):
        # Si es proveedor, recomendamos exigir tipo de tercero para DIOT
        if self.role == 'SUPPLIER' and not self.diot_third_type_id:
            raise ValidationError({
                "diot_third_type": "Requerido para rol Proveedor (DIOT: tipo de tercero)."
            })

    def __str__(self) -> str:
        return f"{self.get_role_display()} - {self.partner.legal_name}"


class PartnerAddress(models.Model):
    """
    Direcciones del Partner. La dirección FISCAL puede diferir de envío.
    En CFDI 4.0, lo mínimo obligatorio para el receptor es el CP fiscal (tax_zip en Partner).
    """
    KIND_CHOICES = [
        ('FISCAL',   'Fiscal'),
        ('SHIPPING', 'Envío'),
        ('OTHER',    'Otra'),
    ]
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='addresses')
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='FISCAL')

    street = models.CharField(max_length=255, blank=True)
    ext_no = models.CharField(max_length=50, blank=True)
    int_no = models.CharField(max_length=50, blank=True)
    neighborhood = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='partner_addresses',
        default='MEX'
    )
    zip_code = models.CharField(max_length=10)

    class Meta:
        indexes = [models.Index(fields=['partner', 'kind'])]
        verbose_name = "Dirección de Partner"
        verbose_name_plural = "Direcciones de Partner"

    def __str__(self) -> str:
        return f"[{self.kind}] {self.partner.legal_name} - CP {self.zip_code}"


class PartnerContact(models.Model):
    """
    Contactos operativos (Compras, CxP, Dirección, Logística, etc.).
    """
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    phone_landline = models.CharField(max_length=30, blank=True, default='', help_text='Teléfono fijo')
    phone_landline_ext = models.CharField(max_length=10, blank=True, default='', help_text='Extensión del teléfono fijo')
    job_position = models.ForeignKey(
        JobPosition, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='partner_contacts'
    )
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'No especificado'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, default='N')
    person_title = models.ForeignKey(
        PersonTitle, null=True, blank=True, on_delete=models.PROTECT,
        related_name='partners', help_text='Título personal (Ing., Lic., Dr., etc.)'
    )
    photo = models.ImageField(upload_to='partners/contacts/', null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['partner', 'email'])]
        verbose_name = "Contacto de Partner"
        verbose_name_plural = "Contactos de Partner"

    def __str__(self) -> str:
        return f"{self.name} ({self.partner.legal_name})"


class PartnerBankAccount(models.Model):
    """
    Cuentas bancarias del Partner (banco normalizado por c_Banco).
    """
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='bank_accounts')
    bank = models.ForeignKey(
        SatCatalog, on_delete=models.PROTECT,
        limit_choices_to={'catalog': 'c_Banco'}
    )
    clabe = models.CharField(max_length=18)
    account_name = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [models.Index(fields=['partner', 'bank'])]
        verbose_name = "Cuenta bancaria de Partner"
        verbose_name_plural = "Cuentas bancarias de Partner"

    def __str__(self) -> str:
        return f"{self.partner.legal_name} - {self.bank.code}"
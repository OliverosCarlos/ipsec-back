from django.core.validators import RegexValidator
from django.db import models

from core.models import BaseModel
from entities.models.catalogs import Bank
from invoicing.models.sat import SatCatalog
from .company import Company


class CompanyBankAccount(BaseModel):
    """Cuentas bancarias de la empresa (mostrables en cotizaciones/facturas)."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='bank_accounts',
    )
    bank = models.ForeignKey(
        Bank, on_delete=models.PROTECT,
    )
    account_number = models.CharField(max_length=30, blank=True)
    clabe = models.CharField(
        max_length=18,
        validators=[RegexValidator(r'^\d{18}$', 'CLABE debe tener 18 dígitos')],
    )
    account_holder = models.CharField(
        max_length=255, blank=True,
        help_text='Titular de la cuenta (si difiere de la razón social)',
    )
    currency = models.ForeignKey(
        SatCatalog, on_delete=models.PROTECT, null=True, blank=True,
        related_name='company_bank_accounts',
        limit_choices_to={'catalog': 'c_Moneda'},
    )
    swift_code = models.CharField(max_length=11, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['company', 'bank'])]
        verbose_name = 'Cuenta bancaria de Empresa'
        verbose_name_plural = 'Cuentas bancarias de Empresa'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'clabe'], name='uniq_company_clabe',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.company.legal_name} - {self.bank.short_name} ({self.clabe[-4:]})'

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from ipsec_back import settings


class QuotationDailySequence(models.Model):
    """Stores the latest quotation sequence generated for each calendar day."""

    sequence_date = models.DateField(unique=True, db_index=True)
    last_sequence = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Quotation Daily Sequence'
        verbose_name_plural = 'Quotation Daily Sequences'

    def __str__(self):
        return f'{self.sequence_date}: {self.last_sequence}'


class Quotation(BaseModel):
    """
    Cotización de venta (Sales Quotation).
    Sigue el flujo estándar de ERPs: Draft → Sent → Confirmed → Cancelled.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        SENT = 'sent', 'Enviada'
        CONFIRMED = 'confirmed', 'Confirmada'
        CANCELLED = 'cancelled', 'Cancelada'

    # --- Propuesta padre (opcional) ---
    proposal = models.ForeignKey(
        'sales.SalesProposal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Propuesta de venta a la que pertenece esta cotización (opcional)',
    )

    # --- Identificación ---
    number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text='Número de cotización (ej. QTN-0001)',
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Referencia del cliente o número de solicitud',
    )

    # --- Entidad / Cliente ---
    partner = models.ForeignKey(
        'entities.Partner',
        on_delete=models.PROTECT,
        related_name='quotations',
        help_text='Cliente al que se emite la cotización',
    )
    partner_contact = models.ForeignKey(
        'entities.PartnerContact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Contacto del cliente',
    )
    shipping_address = models.ForeignKey(
        'entities.PartnerAddress',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Dirección de envío',
    )

    # --- Fechas ---
    date = models.DateField(help_text='Fecha de emisión de la cotización')
    validity_date = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de vencimiento / vigencia',
    )
    expected_closing_date = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha esperada de cierre',
    )

    # --- Condiciones comerciales ---
    currency = models.ForeignKey(
        'invoicing.SatCatalog',
        on_delete=models.PROTECT,
        related_name='quotations_currency',
        limit_choices_to={'catalog': 'c_Moneda'},
        help_text='Moneda (catálogo SAT c_Moneda)',
    )
    payment_terms_days = models.PositiveIntegerField(
        default=0,
        help_text='Días de crédito',
    )
    payment_method = models.ForeignKey(
        'invoicing.SatCatalog',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='quotations_payment_method',
        limit_choices_to={'catalog': 'c_MetodoPago'},
        help_text='Método de pago SAT (PUE, PPD)',
    )
    payment_form = models.ForeignKey(
        'invoicing.SatCatalog',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='quotations_payment_form',
        limit_choices_to={'catalog': 'c_FormaPago'},
        help_text='Forma de pago SAT (01, 02, etc.)',
    )
    price_list = models.ForeignKey(
        'invoicing.PriceList',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Lista de precios aplicada',
    )

    # --- Estado ---
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    # --- Vendedor ---
    salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Vendedor responsable',
    )

    # --- Totales (calculados) ---
    amount_subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Subtotal antes de impuestos',
    )
    amount_discount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Monto total de descuento',
    )
    amount_tax = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total de impuestos',
    )
    amount_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total de la cotización',
    )

    # --- Notas ---
    internal_notes = models.TextField(
        blank=True,
        default='',
        help_text='Notas internas',
    )
    external_notes = models.TextField(
        blank=True,
        default='',
        help_text='Términos y condiciones visibles al cliente',
    )

    class Meta:
        ordering = ['-date', '-number']
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        indexes = [
            models.Index(fields=['partner', 'status']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f'{self.number} - {self.partner.legal_name}'

    def set_salesperson_from_user(self, user):
        """Assign logged-in user as salesperson when the field is empty."""
        if self.salesperson_id is None and user and getattr(user, 'is_authenticated', False):
            self.salesperson = user

    @staticmethod
    def _month_code(value_date):
        month_codes = {
            1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F',
            7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L',
        }
        return month_codes[value_date.month]

    @classmethod
    def _next_daily_sequence(cls, value_date):
        with transaction.atomic():
            try:
                daily_sequence, _ = QuotationDailySequence.objects.select_for_update().get_or_create(
                    sequence_date=value_date,
                    defaults={'last_sequence': 0},
                )
            except IntegrityError:
                daily_sequence = QuotationDailySequence.objects.select_for_update().get(
                    sequence_date=value_date,
                )

            daily_sequence.last_sequence += 1
            daily_sequence.save(update_fields=['last_sequence'])
            return daily_sequence.last_sequence

    @classmethod
    def generate_number(cls, value_date):
        daily_sequence = cls._next_daily_sequence(value_date)
        month_code = cls._month_code(value_date)
        return f'{month_code}{value_date.day:02d}{value_date.year % 100:02d}-{daily_sequence}.1'

    def save(self, *args, **kwargs):
        if not self.number:
            reference_date = self.date or timezone.localdate()
            self.number = self.generate_number(reference_date)
        super().save(*args, **kwargs)

    # --- Cálculo de totales ---
    def compute_totals(self):
        """Recalcula subtotal, descuento, impuestos y total a partir de las líneas."""
        lines = self.lines.all()
        subtotal = Decimal('0.00')
        discount = Decimal('0.00')
        tax = Decimal('0.00')

        for line in lines:
            subtotal += line.subtotal
            discount += line.discount_amount
            tax += line.tax_amount

        self.amount_subtotal = subtotal
        self.amount_discount = discount
        self.amount_tax = tax
        self.amount_total = subtotal - discount + tax
        self.save(update_fields=[
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
        ])


class QuotationLine(BaseModel):
    """Línea de detalle de una cotización."""

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='lines',
    )
    sequence = models.PositiveIntegerField(
        default=10,
        help_text='Orden de la línea en la cotización',
    )

    # --- Producto ---
    product_service_variation = models.ForeignKey(
        'resources.ProdServVariation',
        on_delete=models.PROTECT,
        related_name='quotation_lines',
        help_text='Variación de producto cotizada',
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='Descripción personalizada (override del producto)',
    )

    # --- Cantidades y precios ---
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
    )
    clave_unidad = models.ForeignKey(
        'invoicing.ClaveUnidad',
        on_delete=models.PROTECT,
        related_name='quotation_lines',
        help_text='Unidad de medida SAT',
    )
    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Precio unitario',
    )

    # --- Descuento ---
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Porcentaje de descuento (0-100)',
    )

    # --- Impuestos ---
    tax_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Porcentaje de impuesto (ej. 16 para IVA 16%)',
    )

    class Meta:
        ordering = ['quotation', 'sequence']
        verbose_name = 'Quotation Line'
        verbose_name_plural = 'Quotation Lines'

    def __str__(self):
        return f'{self.quotation.number} - Ln {self.sequence}'

    # --- Propiedades calculadas ---
    @property
    def subtotal(self) -> Decimal:
        """quantity × unit_price"""
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'))

    @property
    def discount_amount(self) -> Decimal:
        """Monto de descuento sobre el subtotal."""
        return (self.subtotal * self.discount_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def taxable_amount(self) -> Decimal:
        """Base gravable: subtotal − descuento."""
        return self.subtotal - self.discount_amount

    @property
    def tax_amount(self) -> Decimal:
        """Importe de impuesto."""
        return (self.taxable_amount * self.tax_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def total(self) -> Decimal:
        """Total de la línea: base gravable + impuesto."""
        return self.taxable_amount + self.tax_amount

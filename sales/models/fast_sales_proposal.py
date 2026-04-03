from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db import transaction

from core.models import BaseModel
from ipsec_back import settings


class FastSalesProposal(BaseModel):
    """
    Propuesta de venta rápida (Fast Sales Proposal).
    Agrupa varias versiones de cotización (FastQuotation) sin necesidad
    de folios oficiales ni un Partner obligatorio.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        IN_PROGRESS = 'in_progress', 'En progreso'
        APPROVED = 'approved', 'Aprobada'
        REJECTED = 'rejected', 'Rechazada'
        CANCELLED = 'cancelled', 'Cancelada'

    # --- Identificación ---
    name = models.CharField(
        max_length=200,
        help_text='Nombre de la propuesta de venta',
    )
    objective = models.TextField(
        blank=True,
        default='',
        help_text='Objetivo de la propuesta de venta',
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Descripción general de la propuesta',
    )

    # --- Partner opcional ---
    partner = models.ForeignKey(
        'entities.Partner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fast_sales_proposals',
        help_text='Cliente asociado (opcional)',
    )
    partner_contact = models.ForeignKey(
        'entities.PartnerContact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fast_sales_proposals',
        help_text='Contacto del cliente (opcional)',
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
        related_name='fast_sales_proposals',
        help_text='Vendedor responsable',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Fast Sales Proposal'
        verbose_name_plural = 'Fast Sales Proposals'
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name


class FastQuotation(BaseModel):
    """
    Cotización rápida (Fast Quotation).
    Versión de cotización dentro de una propuesta de venta rápida.
    No requiere folios ni números de referencia oficiales.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        SENT = 'sent', 'Enviada'
        CONFIRMED = 'confirmed', 'Confirmada'
        CANCELLED = 'cancelled', 'Cancelada'

    # --- Propuesta padre (opcional) ---
    proposal = models.ForeignKey(
        FastSalesProposal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        help_text='Propuesta de venta a la que pertenece esta cotización (opcional)',
    )

    # --- Identificación auxiliar ---
    name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Nombre auxiliar del cliente (sin necesidad de tener un Partner registrado)',
    )
    description = models.CharField(
        max_length=300,
        blank=True,
        default='',
        help_text='Asunto o título de la cotización',
    )

    # --- Fechas ---
    date = models.DateField(help_text='Fecha de emisión de la cotización')
    validity_date = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de vencimiento / vigencia',
    )

    # --- Condiciones comerciales ---
    currency = models.ForeignKey(
        'invoicing.SatCatalog',
        on_delete=models.PROTECT,
        related_name='fast_quotations_currency',
        limit_choices_to={'catalog': 'c_Moneda'},
        help_text='Moneda (catálogo SAT c_Moneda)',
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
        related_name='fast_quotations',
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
        help_text='Notas internas (solo visibles para el equipo)',
    )
    external_notes = models.TextField(
        blank=True,
        default='',
        help_text='Notas externas (visibles para el cliente)',
    )

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Fast Quotation'
        verbose_name_plural = 'Fast Quotations'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        label = self.description or self.name or str(self.id)[:8]
        return f'FQ-{self.pk} - {label}'

    # --- Convertir a propuesta ---
    @transaction.atomic
    def convert_to_proposal(self, name='', objective='', description=''):
        """
        Convierte esta cotización rápida independiente en una FastSalesProposal.
        Si ya pertenece a una propuesta, retorna la propuesta existente.
        """
        if self.proposal is not None:
            return self.proposal

        proposal = FastSalesProposal.objects.create(
            name=name or self.name or f'Propuesta desde FQ-{self.pk}',
            objective=objective,
            description=description or self.description,
            salesperson=self.salesperson,
            status=FastSalesProposal.Status.DRAFT,
        )
        self.proposal = proposal
        self.save(update_fields=['proposal'])
        return proposal

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


class FastQuotationLine(BaseModel):
    """Línea de detalle de una cotización rápida."""

    fast_quotation = models.ForeignKey(
        FastQuotation,
        on_delete=models.CASCADE,
        related_name='lines',
    )
    sequence = models.PositiveIntegerField(
        default=10,
        help_text='Orden de la línea en la cotización',
    )

    # --- Producto ---
    product_variation = models.ForeignKey(
        'resources.ProductVariation',
        on_delete=models.PROTECT,
        related_name='fast_quotation_lines',
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
    unit_of_measure = models.ForeignKey(
        'invoicing.ClaveUnidad',
        on_delete=models.PROTECT,
        related_name='fast_quotation_lines',
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
        ordering = ['fast_quotation', 'sequence']
        verbose_name = 'Fast Quotation Line'
        verbose_name_plural = 'Fast Quotation Lines'

    def __str__(self):
        return f'FQ-{self.fast_quotation.pk} - Ln {self.sequence}'

    # --- Propiedades calculadas ---
    @property
    def subtotal(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal('0.01'))

    @property
    def discount_amount(self) -> Decimal:
        return (self.subtotal * self.discount_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def taxable_amount(self) -> Decimal:
        return self.subtotal - self.discount_amount

    @property
    def tax_amount(self) -> Decimal:
        return (self.taxable_amount * self.tax_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def total(self) -> Decimal:
        return self.taxable_amount + self.tax_amount

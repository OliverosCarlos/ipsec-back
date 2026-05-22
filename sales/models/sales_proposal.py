from django.db import models

from core.models import BaseModel
from ipsec_back import settings


class SalesProposal(BaseModel):
    """
    Propuesta de venta oficial (Sales Proposal).
    Agrupa varias cotizaciones oficiales (Quotation) bajo un mismo expediente.
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

    # --- Partner ---
    partner = models.ForeignKey(
        'entities.Partner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_proposals',
        help_text='Cliente asociado (opcional)',
    )
    partner_contact = models.ForeignKey(
        'entities.PartnerContact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_proposals',
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
        related_name='sales_proposals',
        help_text='Vendedor responsable',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sales Proposal'
        verbose_name_plural = 'Sales Proposals'
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def set_salesperson_from_user(self, user):
        """Assign logged-in user as salesperson when the field is empty."""
        if self.salesperson_id is None and user and getattr(user, 'is_authenticated', False):
            self.salesperson = user

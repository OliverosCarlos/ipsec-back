from django.db import models

from core.models import BaseModel
from invoicing.models.sat import ClaveUnidad


class ServiceCategory(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

class ServiceDetail(BaseModel):
    BILLING_TYPE_FIXED = 'fixed'
    BILLING_TYPE_RECURRING = 'recurring'

    BILLING_TYPE_CHOICES = [
        (BILLING_TYPE_FIXED, 'Fixed'),
        (BILLING_TYPE_RECURRING, 'Recurring'),
    ]

    PERIOD_DAY = 'day'
    PERIOD_WEEK = 'week'
    PERIOD_MONTH = 'month'
    PERIOD_YEAR = 'year'

    RECURRENCE_PERIOD_CHOICES = [
        (PERIOD_DAY, 'Day'),
        (PERIOD_WEEK, 'Week'),
        (PERIOD_MONTH, 'Month'),
        (PERIOD_YEAR, 'Year'),
    ]

    billing_type = models.CharField(
        max_length=10,
        choices=BILLING_TYPE_CHOICES,
        default=BILLING_TYPE_FIXED,
        help_text='Defines if the charge is one-time or recurring.',
    )
    recurrence_every = models.PositiveIntegerField(
        default=1,
        help_text='Recurrence frequency (for recurring services).',
    )
    recurrence_period = models.CharField(
        max_length=10,
        choices=RECURRENCE_PERIOD_CHOICES,
        default=PERIOD_MONTH,
        help_text='Recurrence period unit.',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Service Modality'
        verbose_name_plural = 'Service Modalities'

    def __str__(self):
        return f'{self.service.name} - {self.name}'
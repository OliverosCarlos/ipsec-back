from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    """Cuenta de usuario del sistema. Extiende el User de Django."""

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return self.username


class AccountPlatformSettings(models.Model):
    """Configuracion general por cuenta para personalizar la plataforma."""

    account = models.OneToOneField(
        Account,
        related_name="platform_settings",
        on_delete=models.CASCADE,
    )
    theme = models.CharField(max_length=40, default="light")
    font_family = models.CharField(max_length=80, default="system")
    currency_code = models.CharField(max_length=10, default="MXN")
    locale = models.CharField(max_length=20, default="es-MX")
    preferences = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_account_platform_settings"
        verbose_name = "Account Platform Settings"
        verbose_name_plural = "Account Platform Settings"

    def __str__(self) -> str:
        return f"{self.account.username} settings"
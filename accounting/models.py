from django.db import models


class Account(models.Model):
	class AccountType(models.TextChoices):
		ASSET = 'asset', 'Asset'
		LIABILITY = 'liability', 'Liability'
		EXPENSE = 'expense', 'Expense'
		REVENUE = 'revenue', 'Revenue'

	code = models.CharField(max_length=30, unique=True)
	name = models.CharField(max_length=255)
	account_type = models.CharField(max_length=20, choices=AccountType.choices)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['code']
		verbose_name = 'Account'
		verbose_name_plural = 'Accounts'

	def __str__(self):
		return f'{self.code} - {self.name}'

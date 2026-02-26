from django.db import models


class Supplier(models.Model):
	code = models.CharField(max_length=30, unique=True)
	name = models.CharField(max_length=255)
	tax_id = models.CharField(max_length=50, blank=True, default='')
	email = models.EmailField(blank=True, default='')
	phone = models.CharField(max_length=50, blank=True, default='')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Supplier'
		verbose_name_plural = 'Suppliers'

	def __str__(self):
		return f'{self.name} ({self.code})'

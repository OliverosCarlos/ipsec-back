from django.db import models


class PersonTitle(models.Model):
	"""Catálogo de títulos de persona: Ing., Lic., Mtro., Dr., etc."""
	code = models.CharField(max_length=20, unique=True)
	name = models.CharField(max_length=100)
	abbreviation = models.CharField(max_length=20, blank=True, default='')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Person Title'
		verbose_name_plural = 'Person Titles'

	def __str__(self):
		return self.name


class CompanySector(models.Model):
	"""Catálogo de sectores de empresa: Tecnología, Educación, Salud, etc."""
	code = models.CharField(max_length=20, unique=True)
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=255, blank=True, default='')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Company Sector'
		verbose_name_plural = 'Company Sectors'

	def __str__(self):
		return self.name


class Country(models.Model):
	code = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=100)

	class Meta:
		ordering = ['name']
		verbose_name = 'Country'
		verbose_name_plural = 'Countries'

	def __str__(self):
		return f'{self.code} - {self.name}'


class JobPosition(models.Model):
	"""Catálogo de roles/puestos dentro de una empresa."""
	code = models.CharField(max_length=30, unique=True)
	name = models.CharField(max_length=120)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Job Position'
		verbose_name_plural = 'Job Positions'

	def __str__(self):
		return self.name


class Bank(models.Model):
	"""Catálogo de bancos: clave, nombre corto y razón social."""
	code = models.CharField(max_length=20, unique=True)
	short_name = models.CharField(max_length=100)
	legal_name = models.CharField(max_length=255, blank=True, default='')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['short_name']
		verbose_name = 'Bank'
		verbose_name_plural = 'Banks'

	def __str__(self):
		return f"{self.code} - {self.short_name}"

from django.db import models


class SatCatalog(models.Model):
	"""
	Catálogo SAT genérico para normalizar valores del Anexo 20 (CFDI 4.0),
	p.ej.: c_RegimenFiscal, c_Pais, c_Banco, c_Moneda, c_ClaveProdServ, etc.
	Mantén las vigencias para evitar usar claves fuera de periodo.
	Fuentes: Catálogos CFDI 4.0 (SAT / Anexo 20).
	"""
	code = models.CharField(max_length=20, primary_key=True)
	catalog = models.CharField(max_length=60, db_index=True)
	description = models.CharField(max_length=255)
	valid_from = models.DateField(null=True, blank=True)
	valid_to = models.DateField(null=True, blank=True)

	class Meta:
		indexes = [models.Index(fields=['catalog', 'code'])]
		verbose_name = 'Catálogo SAT'
		verbose_name_plural = 'Catálogos SAT'

	def __str__(self):
		return f'{self.catalog}:{self.code} - {self.description}'
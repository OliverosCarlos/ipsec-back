from django.db import models
from .sat import ClaveProdServ, ClaveUnidad, SatCatalog

class ProdServVariationSAT(models.Model):
	clave_prod_serv = models.ForeignKey(
		ClaveProdServ, null=True, blank=True, on_delete=models.PROTECT,
		related_name='variation_sat',
		help_text="Clave de Producto/Servicio SAT"
	)
	clave_unidad = models.ForeignKey(
		ClaveUnidad, null=True, blank=True, on_delete=models.PROTECT,
		related_name='variation_sat_unidad',
		help_text="Clave de Unidad SAT"
	)
	unidad = models.CharField(max_length=255, blank=True, help_text="Unidad SAT")
	objeto_imp = models.ForeignKey(
		SatCatalog, null=True, blank=True, on_delete=models.PROTECT,
		related_name='variation_sat_objeto_imp',
		limit_choices_to={'catalog': 'c_ObjetoImp'},
		help_text="Objeto de impuesto (01, 02, etc.)"
	)

class PriceList(models.Model):
	code = models.CharField(max_length=30, unique=True)
	name = models.CharField(max_length=255)
	currency = models.CharField(max_length=10, default='USD')
	valid_from = models.DateField(null=True, blank=True)
	valid_to = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Price List'
		verbose_name_plural = 'Price Lists'

	def __str__(self):
		return f'{self.name} ({self.code})'


class PriceListItem(models.Model):
	price_list = models.ForeignKey(
		PriceList,
		on_delete=models.CASCADE,
		related_name='items',
	)
	product_variation = models.ForeignKey(
		'resources.ProdServVariation',
		on_delete=models.CASCADE,
		related_name='price_list_items',
	)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['price_list', 'product_variation']
		verbose_name = 'Price List Item'
		verbose_name_plural = 'Price List Items'
		unique_together = ['price_list', 'product_variation']

	def __str__(self):
		return f'{self.price_list.code} - {self.product_variation}'
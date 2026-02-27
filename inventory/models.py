from django.db import models


class Warehouse(models.Model):
	code = models.CharField(max_length=30, unique=True)
	name = models.CharField(max_length=255)
	address = models.CharField(max_length=255, blank=True, default='')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Warehouse'
		verbose_name_plural = 'Warehouses'

	def __str__(self):
		return f'{self.name} ({self.code})'


class StockItem(models.Model):
	product_variation = models.ForeignKey(
		'resources.ProductVariation',
		on_delete=models.CASCADE,
		related_name='stock_items',
	)
	warehouse = models.ForeignKey(
		Warehouse,
		on_delete=models.PROTECT,
		related_name='stock_items',
	)
	on_hand = models.DecimalField(max_digits=12, decimal_places=4, default=0)
	min_stock = models.DecimalField(max_digits=12, decimal_places=4, default=0)
	max_stock = models.DecimalField(max_digits=12, decimal_places=4, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['warehouse', 'product_variation']
		verbose_name = 'Stock Item'
		verbose_name_plural = 'Stock Items'
		unique_together = ['product_variation', 'warehouse']

	def __str__(self):
		return f'{self.product_variation} @ {self.warehouse.code}'


class StockMovement(models.Model):
	class MovementType(models.TextChoices):
		INBOUND = 'in', 'Inbound'
		OUTBOUND = 'out', 'Outbound'
		ADJUSTMENT = 'adjustment', 'Adjustment'
		TRANSFER = 'transfer', 'Transfer'

	product_variation = models.ForeignKey(
		'resources.ProductVariation',
		on_delete=models.CASCADE,
		related_name='stock_movements',
	)
	warehouse = models.ForeignKey(
		Warehouse,
		on_delete=models.PROTECT,
		related_name='stock_movements',
	)
	movement_type = models.CharField(max_length=20, choices=MovementType.choices)
	quantity = models.DecimalField(max_digits=12, decimal_places=4)
	reference = models.CharField(max_length=100, blank=True, default='')
	note = models.TextField(blank=True, default='')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Stock Movement'
		verbose_name_plural = 'Stock Movements'

	def __str__(self):
		return f'{self.product_variation} {self.movement_type} {self.quantity}'


class StockAdjustment(models.Model):
	product_variation = models.ForeignKey(
		'resources.ProductVariation',
		on_delete=models.CASCADE,
		related_name='stock_adjustments',
	)
	warehouse = models.ForeignKey(
		Warehouse,
		on_delete=models.PROTECT,
		related_name='stock_adjustments',
	)
	quantity = models.DecimalField(max_digits=12, decimal_places=4)
	reason = models.CharField(max_length=255, blank=True, default='')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Stock Adjustment'
		verbose_name_plural = 'Stock Adjustments'

	def __str__(self):
		return f'{self.product_variation} adj {self.quantity}'

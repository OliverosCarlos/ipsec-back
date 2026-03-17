from django.db import models
from django.db.models import JSONField

from core.models import BaseModel

from .general import Brand, Category, Type
from invoicing.models.sat import ClaveUnidad


class Product(BaseModel):
    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=255, blank=True, default='')
    long_description = models.TextField(blank=True, default='')
    
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='products',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
    )
    product_type = models.ForeignKey(
        Type,
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
    )
    partners = models.ManyToManyField(
        'entities.Partner',
        related_name='products',
        blank=True,
    )
    inventory_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
    )

    # Preparación para Facturación (CFDI 4.0 - México)
    sat_product_key = models.CharField(max_length=20, blank=True, help_text="Clave de Producto/Servicio SAT")
    tax_object = models.CharField(max_length=10, blank=True, help_text="Objeto de impuesto (01, 02, etc.)")
    
    # Preparación Contable (Se vinculará después)
    # income_account = models.ForeignKey('accounting.Account',...)
    # expense_account = models.ForeignKey('accounting.Account',...)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.name}'


class ProductVariation(BaseModel):
    product = models.ForeignKey( Product,on_delete=models.CASCADE,related_name='variations', )
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    barcode = models.CharField(max_length=100, blank=True, default='')
    attributes = JSONField(default=dict, blank=True)

    # Campos opcionales para sobrescribir (override) la información del padre
    override_name = models.CharField(max_length=255, blank=True, null=True, help_text="Déjalo en blanco para autogenerar.")
    override_short_description = models.CharField(max_length=500, blank=True, null=True)

    unit_of_measure = models.ForeignKey(
        ClaveUnidad,
        on_delete=models.PROTECT,
        related_name='variations',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    
    # Precios y Costos Base (Escalable a listas de precios complejas)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Precio de venta base")
    standard_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Costo de referencia")

    image = models.ImageField(upload_to='resources/variations/', blank=True, null=True)

    # Preparación para Inventario (Gestión de Series/Lotes)
    # is_serialized = models.BooleanField(default=False)
    # has_batches = models.BooleanField(default=False)

    class Meta:
        ordering = ['product', 'quantity']
        verbose_name = 'Product Variation'
        verbose_name_plural = 'Product Variations'

    def __str__(self):
        attr_str = ", ".join([f"{v}" for k, v in self.attributes.items()])
        return f"{self.product.name} - {attr_str}" if attr_str else f"{self.product.name} (Default)"

    @property
    def display_name(self):
        """Lógica de autogeneración o fallback para el nombre de la variante"""
        if self.override_name:
            return self.override_name
            
        # Autogenerar basado en el padre y los atributos (Ej: "Playera Básica - Rojo - M")
        attr_str = " - ".join([f"{v}" for k, v in self.attributes.items()])
        return f"{self.product.name} - {attr_str}" if attr_str else self.product.name

    @property
    def display_short_description(self):
        """Hereda la descripción del padre si la variante no tiene una propia"""
        return self.override_short_description or self.product.short_description

    @property
    def display_long_description(self):
        """Siempre expone la descripción larga del padre por conveniencia de la API"""
        return self.product.long_description

class PriceList(BaseModel):
    """Módulo CRM/Ventas: Manejo de múltiples monedas y B2B."""
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3, default='MXN')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

class PriceListItem(BaseModel):
    """Sobrescribe el precio base de un SKU para una lista de precios específica."""
    price_list = models.ForeignKey(PriceList, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    override_price = models.DecimalField(max_digits=12, decimal_places=2)
from django.db import models


class Brand(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return f'{self.name} ({self.code})'


class Type(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product Type'
        verbose_name_plural = 'Product Types'

    def __str__(self):
        return f'{self.name} ({self.code})'


class Category(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return f'{self.name} ({self.code})'


class UnitOfMeasure(models.Model):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


class Product(models.Model):
    short_name = models.CharField(max_length=100)
    long_name = models.CharField(max_length=255, blank=True, default='')
    short_description = models.CharField(max_length=255, blank=True, default='')
    long_description = models.TextField(blank=True, default='')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['short_name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.short_name} ({self.sku})'


class ProductVariation(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variations',
    )
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='variations',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    barcode = models.CharField(max_length=100, blank=True, default='')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='resources/variations/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product', 'quantity']
        verbose_name = 'Product Variation'
        verbose_name_plural = 'Product Variations'

    def __str__(self):
        return (
            f'{self.product.short_name} - {self.quantity} '
            f'{self.unit_of_measure.abbreviation}'
        )

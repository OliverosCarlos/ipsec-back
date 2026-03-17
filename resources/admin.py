from django.contrib import admin

from .models import Brand, Product, ProductVariation, UnitOfMeasure


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_active', 'created_at']
    search_fields = ['name', 'abbreviation']
    list_filter = ['is_active']


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['brand', 'is_active']
    inlines = [ProductVariationInline]


@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'unit_of_measure', 'is_active']
    search_fields = ['product__name', 'barcode']
    list_filter = ['is_active', 'unit_of_measure']

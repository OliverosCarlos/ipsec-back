from django.contrib import admin

from .models import Brand, ProdServ, ProdServVariation, UnitOfMeasure


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


class ProdServVariationInline(admin.TabularInline):
    model = ProdServVariation
    extra = 1


@admin.register(ProdServ)
class ProdServAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['brand', 'is_active']
    inlines = [ProdServVariationInline]


@admin.register(ProdServVariation)
class ProdServVariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'is_active']
    search_fields = ['product__name']
    list_filter = ['is_active']

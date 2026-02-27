from rest_framework import serializers

from accounting.serializers import AccountSerializer
from entities.serializers import SupplierSerializer

from .models import (
    Brand,
    Product,
    Category,
    ProductVariation,
    Type,
    UnitOfMeasure,
)


# ── Brand ──────────────────────────────────────────────────────────────────────

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Type ──────────────────────────────────────────────────────────────

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Category ──────────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Unit of Measure ────────────────────────────────────────────────────────────

class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ['id', 'name', 'abbreviation', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Product Variation ─────────────────────────────────────────────────────────

class ProductVariationSerializer(serializers.ModelSerializer):
    unit_of_measure_detail = UnitOfMeasureSerializer(source='unit_of_measure', read_only=True)

    class Meta:
        model = ProductVariation
        fields = [
            'id',
            'product',
            'unit_of_measure',
            'unit_of_measure_detail',
            'quantity',
            'barcode',
            'price',
            'image',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductVariationWriteSerializer(serializers.ModelSerializer):
    """Serializer for nested variation creation/update inside ProductSerializer."""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductVariation
        fields = [
            'id',
            'unit_of_measure',
            'quantity',
            'barcode',
            'price',
            'image',
            'is_active',
        ]


# ── Product ────────────────────────────────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    brand_detail = BrandSerializer(source='brand', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    product_type_detail = TypeSerializer(source='product_type', read_only=True)
    suppliers_detail = SupplierSerializer(source='suppliers', many=True, read_only=True)
    inventory_account_detail = AccountSerializer(source='inventory_account', read_only=True)
    variations = ProductVariationWriteSerializer(many=True, required=False)
    variations_detail = ProductVariationSerializer(source='variations', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'short_name',
            'long_name',
            'short_description',
            'long_description',
            'sku',
            'brand',
            'brand_detail',
            'category',
            'category_detail',
            'product_type',
            'product_type_detail',
            'suppliers',
            'suppliers_detail',
            'inventory_account',
            'inventory_account_detail',
            'is_active',
            'variations',
            'variations_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
        suppliers_data = validated_data.pop('suppliers', [])
        product = Product.objects.create(**validated_data)
        if suppliers_data:
            product.suppliers.set(suppliers_data)
        for variation_data in variations_data:
            variation_data.pop('id', None)
            ProductVariation.objects.create(product=product, **variation_data)
        return product

    def update(self, instance, validated_data):
        variations_data = validated_data.pop('variations', None)
        suppliers_data = validated_data.pop('suppliers', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if suppliers_data is not None:
            instance.suppliers.set(suppliers_data)

        if variations_data is not None:
            existing_ids = set(instance.variations.values_list('id', flat=True))
            incoming_ids = set()

            for variation_data in variations_data:
                variation_id = variation_data.pop('id', None)
                if variation_id and variation_id in existing_ids:
                    # Update existing variation
                    ProductVariation.objects.filter(
                        id=variation_id, product=instance,
                    ).update(**variation_data)
                    incoming_ids.add(variation_id)
                else:
                    # Create new variation
                    ProductVariation.objects.create(
                        product=instance, **variation_data,
                    )

            # Delete variations not included in the request
            to_delete = existing_ids - incoming_ids
            if to_delete:
                instance.variations.filter(id__in=to_delete).delete()

        return instance

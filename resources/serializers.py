from rest_framework import serializers

from accounting.serializers import AccountSerializer
from entities.serializers import PartnerSerializer

from .models import (
    Brand,
    Product,
    Category,
    PriceList,
    PriceListItem,
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
    unit_of_measure_detail = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)

    display_short_description = serializers.CharField(read_only=True)
    display_long_description = serializers.CharField(read_only=True)

    class Meta:
        model = ProductVariation
        fields = [
            'id',
            'product',
            'sku',
            'barcode',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'unit_of_measure',
            'unit_of_measure_detail',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'display_name',
            'display_short_description',
            'display_long_description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_unit_of_measure_detail(self, obj):
        from invoicing.serializers import ClaveUnidadSerializer
        return ClaveUnidadSerializer(obj.unit_of_measure).data if obj.unit_of_measure else None
    

class ProductVariationWriteSerializer(serializers.ModelSerializer):
    """Serializer for nested variation creation/update inside ProductSerializer."""
    id = serializers.UUIDField(required=False)

    class Meta:
        model = ProductVariation
        fields = [
            'id',
            'sku',
            'barcode',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'unit_of_measure',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'is_active',
        ]


# ── Product ────────────────────────────────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    brand_detail = BrandSerializer(source='brand', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    product_type_detail = TypeSerializer(source='product_type', read_only=True)
    partners_detail = PartnerSerializer(source='partners', many=True, read_only=True)
    inventory_account_detail = AccountSerializer(source='inventory_account', read_only=True)
    variations = ProductVariationWriteSerializer(many=True, required=False)
    variations_detail = ProductVariationSerializer(source='variations', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'short_description',
            'long_description',
            'sat_product_key',
            'tax_object',
            'brand',
            'brand_detail',
            'category',
            'category_detail',
            'product_type',
            'product_type_detail',
            'partners',
            'partners_detail',
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
        partners_data = validated_data.pop('partners', [])
        product = Product.objects.create(**validated_data)
        if partners_data:
            product.partners.set(partners_data)
        for variation_data in variations_data:
            variation_data.pop('id', None)
            ProductVariation.objects.create(product=product, **variation_data)
        return product

    def update(self, instance, validated_data):
        variations_data = validated_data.pop('variations', None)
        partners_data = validated_data.pop('partners', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if partners_data is not None:
            instance.partners.set(partners_data)

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


# ── PriceList ──────────────────────────────────────────────────────────────────

class PriceListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceListItem
        fields = ['id', 'price_list', 'variant', 'override_price', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PriceListSerializer(serializers.ModelSerializer):
    items = PriceListItemSerializer(many=True, read_only=True)

    class Meta:
        model = PriceList
        fields = ['id', 'name', 'currency', 'start_date', 'end_date', 'items', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

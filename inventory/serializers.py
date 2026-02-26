from rest_framework import serializers

from resources.serializers import ProductVariationSerializer

from .models import StockAdjustment, StockItem, StockMovement, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'code', 'name', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockItemSerializer(serializers.ModelSerializer):
    product_variation_detail = ProductVariationSerializer(source='product_variation', read_only=True)
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = StockItem
        fields = [
            'id',
            'product_variation',
            'product_variation_detail',
            'warehouse',
            'warehouse_detail',
            'on_hand',
            'min_stock',
            'max_stock',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    product_variation_detail = ProductVariationSerializer(source='product_variation', read_only=True)
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id',
            'product_variation',
            'product_variation_detail',
            'warehouse',
            'warehouse_detail',
            'movement_type',
            'quantity',
            'reference',
            'note',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StockAdjustmentSerializer(serializers.ModelSerializer):
    product_variation_detail = ProductVariationSerializer(source='product_variation', read_only=True)
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = StockAdjustment
        fields = [
            'id',
            'product_variation',
            'product_variation_detail',
            'warehouse',
            'warehouse_detail',
            'quantity',
            'reason',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

from rest_framework import serializers

# from resources.serializers import ProductVariationSerializer

from .models import ClaveProdServ, ClaveUnidad, PriceList, PriceListItem, SatCatalog


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = [
            'id',
            'code',
            'name',
            'currency',
            'valid_from',
            'valid_to',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PriceListItemSerializer(serializers.ModelSerializer):
    price_list_detail = PriceListSerializer(source='price_list', read_only=True)
    # product_variation_detail = ProductVariationSerializer(source='product_variation', read_only=True)

    class Meta:
        model = PriceListItem
        fields = [
            'id',
            'price_list',
            'price_list_detail',
            'product_variation',
            # 'product_variation_detail',
            'price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SatCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatCatalog
        fields = [
            'id',
            'code',
            'catalog',
            'description',
            'valid_from',
            'valid_to',
        ]


class SatCatalogBulkCreateSerializer(serializers.ListSerializer):
    child = SatCatalogSerializer()


class ClaveProdServSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaveProdServ
        fields = [
            'clave',
            'descripcion',
            'incluir_iva_trasladado',
            'incluir_ieps_trasladado',
            'palabras_similares',
        ]


class ClaveProdServSearchSerializer(serializers.ModelSerializer):
    similarity = serializers.FloatField(read_only=True)

    class Meta:
        model = ClaveProdServ
        fields = [
            'clave',
            'descripcion',
            'incluir_iva_trasladado',
            'incluir_ieps_trasladado',
            'palabras_similares',
            'similarity',
        ]


class ClaveUnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaveUnidad
        fields = [
            'clave',
            'name',
        ]


class ClaveUnidadSearchSerializer(serializers.ModelSerializer):
    similarity = serializers.FloatField(read_only=True)

    class Meta:
        model = ClaveUnidad
        fields = [
            'clave',
            'name',
            'similarity',
        ]

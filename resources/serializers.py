from rest_framework import serializers

from entities.serializers import PartnerSerializer
from inventory.models import ProductVariationInventory
from invoicing.models.general import ProdServVariationSAT
from invoicing.models.sat import ClaveProdServ, ClaveUnidad, SatCatalog

from .models import (
    Brand,
    ProdServ,
    Category,
    PriceList,
    PriceListItem,
    ProdServVariation,
    ServiceCategory,
    ServiceDetail,
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


# ── SAT Catalogs (read) ───────────────────────────────────────────────────────

class ClaveProdServSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaveProdServ
        fields = ['clave', 'descripcion']
        read_only_fields = fields


class ClaveUnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaveUnidad
        fields = ['clave', 'name']
        read_only_fields = fields


class SatCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatCatalog
        fields = ['id', 'code', 'catalog', 'description']
        read_only_fields = fields


# ── SAT Detail (read) ─────────────────────────────────────────────────────────

class ProdServVariationSATSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdServVariationSAT
        fields = ['id', 'clave_prod_serv', 'clave_unidad', 'unidad', 'objeto_imp']
        read_only_fields = fields


class ProdServVariationSATReadSerializer(serializers.ModelSerializer):
    clave_prod_serv_display = serializers.SerializerMethodField()
    clave_unidad_display = serializers.SerializerMethodField()
    objeto_imp_display = serializers.SerializerMethodField()
    clave_prod_serv_detail = ClaveProdServSerializer(source='clave_prod_serv', read_only=True)
    clave_unidad_detail = ClaveUnidadSerializer(source='clave_unidad', read_only=True)
    objeto_imp_detail = SatCatalogSerializer(source='objeto_imp', read_only=True)

    class Meta:
        model = ProdServVariationSAT
        fields = [
            'id',
            'clave_prod_serv', 'clave_prod_serv_display', 'clave_prod_serv_detail',
            'clave_unidad', 'clave_unidad_display', 'clave_unidad_detail',
            'unidad',
            'objeto_imp', 'objeto_imp_display', 'objeto_imp_detail',
        ]
        read_only_fields = fields

    def get_clave_prod_serv_display(self, obj):
        return str(obj.clave_prod_serv) if obj.clave_prod_serv else None

    def get_clave_unidad_display(self, obj):
        return str(obj.clave_unidad) if obj.clave_unidad else None

    def get_objeto_imp_display(self, obj):
        return str(obj.objeto_imp) if obj.objeto_imp else None


# ── Inventory Detail (read) ───────────────────────────────────────────────────

class ProductVariationInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariationInventory
        fields = ['id', 'sku', 'barcode', 'description']
        read_only_fields = fields


# ── Service Detail (read) ─────────────────────────────────────────────────────

class ServiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDetail
        fields = ['id', 'billing_type', 'recurrence_every', 'recurrence_period', 'is_active', 'created_at', 'updated_at']
        read_only_fields = fields


# ── Product Variation ─────────────────────────────────────────────────────────

class ProdServVariationSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    display_short_description = serializers.CharField(read_only=True)
    display_long_description = serializers.CharField(read_only=True)
    sat_detail = ProdServVariationSATSerializer(read_only=True)
    inventory_detail = ProductVariationInventorySerializer(read_only=True)

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'product',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'service_detail',
            'sat_detail',
            'inventory_detail',
            'display_name',
            'display_short_description',
            'display_long_description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProdServVariationReadSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    display_short_description = serializers.CharField(read_only=True)
    display_long_description = serializers.CharField(read_only=True)
    sat_detail = ProdServVariationSATReadSerializer(read_only=True)
    inventory_detail = ProductVariationInventorySerializer(read_only=True)
    service_detail = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'product',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'service_detail',
            'sat_detail',
            'inventory_detail',
            'display_name',
            'display_short_description',
            'display_long_description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
    

class ProdServVariationWriteSerializer(serializers.ModelSerializer):
    """Serializer for nested variation creation/update inside ProdServSerializer."""
    id = serializers.UUIDField(required=False)

    # SAT fields (clave_unidad, unidad come per-variation)
    clave_unidad = serializers.CharField(max_length=20, required=False, default='')
    unidad = serializers.CharField(max_length=255, required=False, default='')

    # Inventory fields
    sku = serializers.CharField(max_length=100, required=False, default='')
    barcode = serializers.CharField(max_length=100, required=False, default='')
    inventory_description = serializers.CharField(max_length=100, required=False, default='')

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'service_detail',
            'is_active',
            # SAT per-variation
            'clave_unidad',
            'unidad',
            # Inventory per-variation
            'sku',
            'barcode',
            'inventory_description',
        ]


# ── Product ────────────────────────────────────────────────────────────────────

class ProdServReadSerializer(serializers.ModelSerializer):
    brand_detail = BrandSerializer(source='brand', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    product_type_detail = TypeSerializer(source='product_type', read_only=True)
    partners_detail = PartnerSerializer(source='partners', many=True, read_only=True)
    variations = ProdServVariationReadSerializer(many=True, read_only=True)

    class Meta:
        model = ProdServ
        fields = [
            'id',
            'name',
            'short_description',
            'long_description',
            'brand',
            'brand_detail',
            'category',
            'category_detail',
            'product_type',
            'product_type_detail',
            'partners',
            'partners_detail',
            'is_active',
            'variations',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ProdServWriteSerializer(serializers.ModelSerializer):
    variations = ProdServVariationWriteSerializer(many=True, required=False)

    # SAT fields at product level
    clave_prod_serv = serializers.CharField(max_length=20, required=False, default='')
    objeto_imp = serializers.CharField(max_length=10, required=False, default='')

    class Meta:
        model = ProdServ
        fields = [
            'id',
            'name',
            'short_description',
            'long_description',
            'brand',
            'category',
            'product_type',
            'partners',
            'is_active',
            'variations',
            'clave_prod_serv',
            'objeto_imp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _extract_sat_fields(self, variation_data):
        return {
            'clave_unidad': variation_data.pop('clave_unidad', ''),
            'unidad': variation_data.pop('unidad', ''),
        }

    def _extract_inventory_fields(self, variation_data):
        return {
            'sku': variation_data.pop('sku', ''),
            'barcode': variation_data.pop('barcode', ''),
            'description': variation_data.pop('inventory_description', ''),
        }

    def _resolve_sat_catalog(self, catalog, pk):
        if not pk:
            return None
        return SatCatalog.objects.filter(catalog=catalog, pk=pk).first()

    def _create_sat_detail(self, clave_prod_serv, objeto_imp, sat_fields):
        clave_unidad_code = sat_fields.pop('clave_unidad', '')
        return ProdServVariationSAT.objects.create(
            clave_prod_serv_id=clave_prod_serv or None,
            objeto_imp=self._resolve_sat_catalog('c_ObjetoImp', objeto_imp),
            clave_unidad_id=clave_unidad_code or None,
            **sat_fields,
        )

    def _create_inventory_detail(self, inventory_fields):
        if not inventory_fields.get('sku'):
            return None
        return ProductVariationInventory.objects.create(**inventory_fields)

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
        partners_data = validated_data.pop('partners', [])
        clave_prod_serv = validated_data.pop('clave_prod_serv', '')
        objeto_imp = validated_data.pop('objeto_imp', '')

        product = ProdServ.objects.create(**validated_data)
        if partners_data:
            product.partners.set(partners_data)

        for variation_data in variations_data:
            variation_data.pop('id', None)
            sat_fields = self._extract_sat_fields(variation_data)
            inventory_fields = self._extract_inventory_fields(variation_data)

            sat_detail = self._create_sat_detail(clave_prod_serv, objeto_imp, sat_fields)
            inventory_detail = self._create_inventory_detail(inventory_fields)

            ProdServVariation.objects.create(
                product=product,
                sat_detail=sat_detail,
                inventory_detail=inventory_detail,
                **variation_data,
            )
        return product

    def update(self, instance, validated_data):
        variations_data = validated_data.pop('variations', None)
        partners_data = validated_data.pop('partners', None)
        clave_prod_serv = validated_data.pop('clave_prod_serv', '')
        objeto_imp = validated_data.pop('objeto_imp', '')

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
                sat_fields = self._extract_sat_fields(variation_data)
                inventory_fields = self._extract_inventory_fields(variation_data)

                if variation_id and variation_id in existing_ids:
                    # Update existing variation's SAT detail
                    variation = ProdServVariation.objects.get(id=variation_id, product=instance)
                    if variation.sat_detail:
                        clave_unidad_code = sat_fields.pop('clave_unidad', '')
                        update_kwargs = {'unidad': sat_fields.get('unidad', '')}
                        update_kwargs['clave_prod_serv_id'] = clave_prod_serv or variation.sat_detail.clave_prod_serv_id
                        objeto_imp_instance = self._resolve_sat_catalog('c_ObjetoImp', objeto_imp)
                        update_kwargs['objeto_imp'] = objeto_imp_instance if objeto_imp_instance else variation.sat_detail.objeto_imp
                        clave_unidad_instance = ClaveUnidad.objects.filter(clave=clave_unidad_code).first()
                        update_kwargs['clave_unidad'] = clave_unidad_instance if clave_unidad_instance else variation.sat_detail.clave_unidad
                        ProdServVariationSAT.objects.filter(id=variation.sat_detail_id).update(**update_kwargs)
                    else:
                        variation.sat_detail = self._create_sat_detail(clave_prod_serv, objeto_imp, sat_fields)

                    # Update existing variation's inventory detail
                    if variation.inventory_detail and inventory_fields.get('sku'):
                        ProductVariationInventory.objects.filter(id=variation.inventory_detail_id).update(**inventory_fields)
                    elif not variation.inventory_detail and inventory_fields.get('sku'):
                        variation.inventory_detail = self._create_inventory_detail(inventory_fields)

                    # Update the variation itself
                    for attr, value in variation_data.items():
                        setattr(variation, attr, value)
                    variation.save()
                    incoming_ids.add(variation_id)
                else:
                    # Create new variation
                    sat_detail = self._create_sat_detail(clave_prod_serv, objeto_imp, sat_fields)
                    inventory_detail = self._create_inventory_detail(inventory_fields)
                    ProdServVariation.objects.create(
                        product=instance,
                        sat_detail=sat_detail,
                        inventory_detail=inventory_detail,
                        **variation_data,
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


# ── Service Category ──────────────────────────────────────────────────────────

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Service Variation ─────────────────────────────────────────────────────────

class ServiceVariationSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    display_short_description = serializers.CharField(read_only=True)
    display_long_description = serializers.CharField(read_only=True)
    sat_detail = ProdServVariationSATSerializer(read_only=True)
    service_detail = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'product',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'service_detail',
            'sat_detail',
            'display_name',
            'display_short_description',
            'display_long_description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceVariationReadSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    display_short_description = serializers.CharField(read_only=True)
    display_long_description = serializers.CharField(read_only=True)
    sat_detail = ProdServVariationSATReadSerializer(read_only=True)
    service_detail = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'product',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'service_detail',
            'sat_detail',
            'display_name',
            'display_short_description',
            'display_long_description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ServiceDetailWriteSerializer(serializers.Serializer):
    billing_type = serializers.ChoiceField(
        choices=ServiceDetail.BILLING_TYPE_CHOICES, required=False, default='fixed',
    )
    recurrence_every = serializers.IntegerField(required=False, default=1)
    recurrence_period = serializers.ChoiceField(
        choices=ServiceDetail.RECURRENCE_PERIOD_CHOICES, required=False, default='month',
    )


class ServiceVariationWriteSerializer(serializers.ModelSerializer):
    """Serializer for nested variation creation/update inside ServiceWriteSerializer."""
    id = serializers.UUIDField(required=False)

    # SAT fields (clave_unidad, unidad come per-variation)
    clave_unidad = serializers.CharField(max_length=20, required=False, default='')
    unidad = serializers.CharField(max_length=255, required=False, default='')

    # ServiceDetail as nested dict
    service_detail = ServiceDetailWriteSerializer(required=False, default={})

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'base_price',
            'standard_cost',
            'image',
            'is_active',
            # SAT per-variation
            'clave_unidad',
            'unidad',
            # ServiceDetail per-variation
            'service_detail',
        ]


# ── Service (ProdServ) ────────────────────────────────────────────────────────

class ServiceReadSerializer(serializers.ModelSerializer):
    brand_detail = BrandSerializer(source='brand', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    product_type_detail = TypeSerializer(source='product_type', read_only=True)
    partners_detail = PartnerSerializer(source='partners', many=True, read_only=True)
    variations = ServiceVariationReadSerializer(many=True, read_only=True)

    class Meta:
        model = ProdServ
        fields = [
            'id',
            'name',
            'short_description',
            'long_description',
            'brand',
            'brand_detail',
            'category',
            'category_detail',
            'product_type',
            'product_type_detail',
            'partners',
            'partners_detail',
            'is_active',
            'variations',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ServiceWriteSerializer(serializers.ModelSerializer):
    variations = ServiceVariationWriteSerializer(many=True, required=False)

    # SAT fields at product level
    clave_prod_serv = serializers.CharField(max_length=20, required=False, default='')
    objeto_imp = serializers.CharField(max_length=10, required=False, default='')

    class Meta:
        model = ProdServ
        fields = [
            'id',
            'name',
            'short_description',
            'long_description',
            'category',
            'product_type',
            'is_active',
            'variations',
            'clave_prod_serv',
            'objeto_imp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _extract_sat_fields(self, variation_data):
        return {
            'clave_unidad': variation_data.pop('clave_unidad', ''),
            'unidad': variation_data.pop('unidad', ''),
        }

    def _extract_service_detail_fields(self, variation_data):
        detail = variation_data.pop('service_detail', {})
        return {
            'billing_type': detail.get('billing_type', 'fixed'),
            'recurrence_every': detail.get('recurrence_every', 1),
            'recurrence_period': detail.get('recurrence_period', 'month'),
        }

    def _resolve_sat_catalog(self, catalog, pk):
        if not pk:
            return None
        return SatCatalog.objects.filter(catalog=catalog, pk=pk).first()

    def _create_sat_detail(self, clave_prod_serv, objeto_imp, sat_fields):
        clave_unidad_code = sat_fields.pop('clave_unidad', '')
        return ProdServVariationSAT.objects.create(
            clave_prod_serv_id=clave_prod_serv or None,
            objeto_imp=self._resolve_sat_catalog('c_ObjetoImp', objeto_imp),
            clave_unidad_id=clave_unidad_code or None,
            **sat_fields,
        )

    def _create_service_detail(self, service_detail_fields):
        return ServiceDetail.objects.create(**service_detail_fields)

    def create(self, validated_data):
        variations_data = validated_data.pop('variations', [])
        partners_data = validated_data.pop('partners', [])
        clave_prod_serv = validated_data.pop('clave_prod_serv', '')
        objeto_imp = validated_data.pop('objeto_imp', '')

        service = ProdServ.objects.create(**validated_data)
        if partners_data:
            service.partners.set(partners_data)

        for variation_data in variations_data:
            variation_data.pop('id', None)
            sat_fields = self._extract_sat_fields(variation_data)
            service_detail_fields = self._extract_service_detail_fields(variation_data)

            sat_detail = self._create_sat_detail(clave_prod_serv, objeto_imp, sat_fields)
            service_detail = self._create_service_detail(service_detail_fields)

            ProdServVariation.objects.create(
                product=service,
                sat_detail=sat_detail,
                service_detail=service_detail,
                **variation_data,
            )
        return service

    def update(self, instance, validated_data):
        variations_data = validated_data.pop('variations', None)
        partners_data = validated_data.pop('partners', None)
        clave_prod_serv = validated_data.pop('clave_prod_serv', '')
        objeto_imp = validated_data.pop('objeto_imp', '')

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
                sat_fields = self._extract_sat_fields(variation_data)
                service_detail_fields = self._extract_service_detail_fields(variation_data)

                if variation_id and variation_id in existing_ids:
                    variation = ProdServVariation.objects.get(id=variation_id, product=instance)
                    if variation.sat_detail:
                        clave_unidad_code = sat_fields.pop('clave_unidad', '')
                        update_kwargs = {'unidad': sat_fields.get('unidad', '')}
                        update_kwargs['clave_prod_serv_id'] = clave_prod_serv or variation.sat_detail.clave_prod_serv_id
                        objeto_imp_instance = self._resolve_sat_catalog('c_ObjetoImp', objeto_imp)
                        update_kwargs['objeto_imp'] = objeto_imp_instance if objeto_imp_instance else variation.sat_detail.objeto_imp
                        clave_unidad_instance = ClaveUnidad.objects.filter(clave=clave_unidad_code).first()
                        update_kwargs['clave_unidad'] = clave_unidad_instance if clave_unidad_instance else variation.sat_detail.clave_unidad
                        ProdServVariationSAT.objects.filter(id=variation.sat_detail_id).update(**update_kwargs)
                    else:
                        variation.sat_detail = self._create_sat_detail(clave_prod_serv, objeto_imp, sat_fields)

                    # Update or create ServiceDetail
                    if variation.service_detail:
                        ServiceDetail.objects.filter(id=variation.service_detail_id).update(**service_detail_fields)
                    else:
                        variation.service_detail = self._create_service_detail(service_detail_fields)

                    for attr, value in variation_data.items():
                        setattr(variation, attr, value)
                    variation.save()
                    incoming_ids.add(variation_id)
                else:
                    sat_detail = self._create_sat_detail(clave_prod_serv, objeto_imp, sat_fields)
                    service_detail = self._create_service_detail(service_detail_fields)
                    ProdServVariation.objects.create(
                        product=instance,
                        sat_detail=sat_detail,
                        service_detail=service_detail,
                        **variation_data,
                    )

            to_delete = existing_ids - incoming_ids
            if to_delete:
                instance.variations.filter(id__in=to_delete).delete()

        return instance


# ── Product Bulk Update ────────────────────────────────────────────────────────

ACTION_CHOICES = [('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted')]


class _BulkItemMixin(serializers.Serializer):
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        action = attrs.get('action')
        if action in ('updated', 'deleted') and not attrs.get('id'):
            raise serializers.ValidationError({'id': 'Required for action "updated" or "deleted".'})
        return attrs


class ProdServVariationBulkItemSerializer(_BulkItemMixin):
    attributes = serializers.JSONField(required=False, default=dict)
    reference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    override_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    override_short_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=4, required=False, allow_null=True)
    base_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    standard_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    image = serializers.ImageField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)

    # SAT per-variation
    clave_unidad = serializers.CharField(max_length=20, required=False, default='')
    unidad = serializers.CharField(max_length=255, required=False, default='')

    # Inventory per-variation
    sku = serializers.CharField(max_length=100, required=False, default='')
    barcode = serializers.CharField(max_length=100, required=False, default='')
    inventory_description = serializers.CharField(max_length=100, required=False, default='')

    # Service detail per-variation (optional)
    service_detail = serializers.PrimaryKeyRelatedField(
        queryset=ServiceDetail.objects.all(), required=False, allow_null=True,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created' and attrs.get('base_price') is None:
            raise serializers.ValidationError({'base_price': 'Required for action "created".'})
        return attrs


class ProductBulkUpdateSerializer(serializers.Serializer):
    # ProdServ fields (all optional)
    name = serializers.CharField(required=False)
    short_description = serializers.CharField(required=False, allow_blank=True)
    long_description = serializers.CharField(required=False, allow_blank=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    product_type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all(), required=False, allow_null=True)
    partners = serializers.PrimaryKeyRelatedField(
        queryset=ProdServ.partners.field.related_model.objects.all(),
        many=True, required=False,
    )
    is_active = serializers.BooleanField(required=False)

    # SAT fields at product level
    clave_prod_serv = serializers.CharField(max_length=20, required=False, default='')
    objeto_imp = serializers.CharField(max_length=10, required=False, default='')

    # Nested variations with action flags
    variations = ProdServVariationBulkItemSerializer(many=True, required=False)


# ── Service Bulk Update ───────────────────────────────────────────────────────

class ServiceVariationBulkItemSerializer(_BulkItemMixin):
    attributes = serializers.JSONField(required=False, default=dict)
    reference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    override_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    override_short_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    base_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    standard_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    image = serializers.ImageField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)

    # SAT per-variation
    clave_unidad = serializers.CharField(max_length=20, required=False, default='')
    unidad = serializers.CharField(max_length=255, required=False, default='')

    # ServiceDetail per-variation (nested dict)
    service_detail = ServiceDetailWriteSerializer(required=False, default={})

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created' and attrs.get('base_price') is None:
            raise serializers.ValidationError({'base_price': 'Required for action "created".'})
        return attrs


class ServiceBulkUpdateSerializer(serializers.Serializer):
    # ProdServ (Service) fields (all optional)
    name = serializers.CharField(required=False)
    short_description = serializers.CharField(required=False, allow_blank=True)
    long_description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    product_type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all(), required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)

    # SAT fields at product level
    clave_prod_serv = serializers.CharField(max_length=20, required=False, default='')
    objeto_imp = serializers.CharField(max_length=10, required=False, default='')

    # Nested variations with action flags
    variations = ServiceVariationBulkItemSerializer(many=True, required=False)


# ── Unified Resource Item ─────────────────────────────────────────────────────

class ProdServBriefSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', read_only=True, default=None)
    category = serializers.CharField(source='category.name', read_only=True, default=None)
    product_type = serializers.CharField(source='product_type.name', read_only=True, default=None)
    partners_detail = PartnerSerializer(source='partners', many=True, read_only=True)

    class Meta:
        model = ProdServ
        fields = [
            'id',
            'name',
            'short_description',
            'long_description',
            'brand',
            'category',
            'product_type',
            'partners',
            'partners_detail',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ResourceItemSerializer(serializers.ModelSerializer):
    product = ProdServBriefSerializer(read_only=True)
    display_name = serializers.CharField(read_only=True)
    display_short_description = serializers.CharField(read_only=True)
    display_long_description = serializers.CharField(read_only=True)
    sat_detail = ProdServVariationSATReadSerializer(read_only=True)
    inventory_detail = ProductVariationInventorySerializer(read_only=True)
    service_detail = ServiceDetailSerializer(read_only=True)

    class Meta:
        model = ProdServVariation
        fields = [
            'id',
            'product',
            'attributes',
            'reference',
            'override_name',
            'override_short_description',
            'quantity',
            'base_price',
            'standard_cost',
            'image',
            'service_detail',
            'sat_detail',
            'inventory_detail',
            'display_name',
            'display_short_description',
            'display_long_description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

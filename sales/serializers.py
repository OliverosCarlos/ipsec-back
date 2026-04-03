from rest_framework import serializers

from entities.serializers import (
    PartnerAddressNestedSerializer,
    PartnerContactNestedSerializer,
)
from invoicing.serializers import ClaveUnidadSerializer
from resources.serializers import ProductVariationSerializer

from .models import Quotation, QuotationLine, FastSalesProposal, FastQuotation, FastQuotationLine


# ── QuotationLine ──────────────────────────────────────────────

class QuotationLineSerializer(serializers.ModelSerializer):
    """Serializer for standalone QuotationLine CRUD."""
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    taxable_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    product_variation_detail = ProductVariationSerializer(source='product_variation', read_only=True)
    unit_of_measure_detail = ClaveUnidadSerializer(source='unit_of_measure', read_only=True)

    class Meta:
        model = QuotationLine
        fields = [
            'id', 'quotation', 'sequence',
            'product_variation', 'product_variation_detail',
            'description',
            'quantity', 'unit_of_measure', 'unit_of_measure_detail',
            'unit_price', 'discount_percent', 'tax_percent',
            'subtotal', 'discount_amount', 'taxable_amount', 'tax_amount', 'total',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuotationLineNestedSerializer(serializers.ModelSerializer):
    """Serializer for lines nested inside QuotationSerializer (no quotation field)."""
    id = serializers.UUIDField(required=False)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    taxable_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = QuotationLine
        fields = [
            'id', 'sequence',
            'product_variation', 'description',
            'quantity', 'unit_of_measure', 'unit_price',
            'discount_percent', 'tax_percent',
            'subtotal', 'discount_amount', 'taxable_amount', 'tax_amount', 'total',
            'is_active',
        ]


# ── Quotation ──────────────────────────────────────────────────

class QuotationSerializer(serializers.ModelSerializer):
    """Write serializer – accepts nested lines for create/update."""
    lines = QuotationLineNestedSerializer(many=True, required=False)

    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'reference',
            'partner', 'partner_contact', 'shipping_address',
            'date', 'validity_date', 'expected_closing_date',
            'currency', 'payment_terms_days',
            'payment_method', 'payment_form', 'price_list',
            'status', 'salesperson',
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'notes', 'terms_and_conditions',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'created_at', 'updated_at',
        ]

    # ── Nested create / update ─────────────────────────────────

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        quotation = Quotation.objects.create(**validated_data)

        for line_data in lines_data:
            line_data.pop('id', None)
            QuotationLine.objects.create(quotation=quotation, **line_data)

        quotation.compute_totals()
        return quotation

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            existing_ids = set(instance.lines.values_list('id', flat=True))
            incoming_ids = set()

            for line_data in lines_data:
                line_id = line_data.pop('id', None)
                if line_id and line_id in existing_ids:
                    QuotationLine.objects.filter(id=line_id, quotation=instance).update(**line_data)
                    incoming_ids.add(line_id)
                else:
                    QuotationLine.objects.create(quotation=instance, **line_data)

            to_delete = existing_ids - incoming_ids
            if to_delete:
                instance.lines.filter(id__in=to_delete).delete()

        instance.compute_totals()
        return instance


class QuotationReadSerializer(serializers.ModelSerializer):
    """Read-only serializer with expanded related fields."""
    lines = QuotationLineSerializer(many=True, read_only=True)

    partner_display = serializers.CharField(source='partner.legal_name', read_only=True)
    partner_rfc = serializers.CharField(source='partner.rfc', read_only=True)
    partner_contact_display = serializers.CharField(source='partner_contact.name', default=None, read_only=True)
    shipping_address_display = serializers.SerializerMethodField()
    currency_display = serializers.CharField(source='currency.description', read_only=True)
    payment_method_display = serializers.CharField(source='payment_method.description', default=None, read_only=True)
    payment_form_display = serializers.CharField(source='payment_form.description', default=None, read_only=True)
    price_list_display = serializers.CharField(source='price_list.name', default=None, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    salesperson_display = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'reference',
            'partner', 'partner_display', 'partner_rfc',
            'partner_contact', 'partner_contact_display',
            'shipping_address', 'shipping_address_display',
            'date', 'validity_date', 'expected_closing_date',
            'currency', 'currency_display',
            'payment_terms_days',
            'payment_method', 'payment_method_display',
            'payment_form', 'payment_form_display',
            'price_list', 'price_list_display',
            'status', 'status_display',
            'salesperson', 'salesperson_display',
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'notes', 'terms_and_conditions',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]

    def get_shipping_address_display(self, obj):
        if obj.shipping_address:
            return f'[{obj.shipping_address.kind}] CP {obj.shipping_address.zip_code}'
        return None

    def get_salesperson_display(self, obj):
        if obj.salesperson:
            full = obj.salesperson.get_full_name()
            return full if full else obj.salesperson.username
        return None


# ── FastQuotationLine ──────────────────────────────────────────

class FastQuotationLineSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    taxable_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    product_variation_detail = ProductVariationSerializer(source='product_variation', read_only=True)
    unit_of_measure_detail = ClaveUnidadSerializer(source='unit_of_measure', read_only=True)

    class Meta:
        model = FastQuotationLine
        fields = [
            'id', 'fast_quotation', 'sequence',
            'product_variation', 'product_variation_detail',
            'description',
            'quantity', 'unit_of_measure', 'unit_of_measure_detail',
            'unit_price', 'discount_percent', 'tax_percent',
            'subtotal', 'discount_amount', 'taxable_amount', 'tax_amount', 'total',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FastQuotationLineNestedSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    taxable_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = FastQuotationLine
        fields = [
            'id', 'sequence',
            'product_variation', 'description',
            'quantity', 'unit_of_measure', 'unit_price',
            'discount_percent', 'tax_percent',
            'subtotal', 'discount_amount', 'taxable_amount', 'tax_amount', 'total',
            'is_active',
        ]


# ── FastQuotation ──────────────────────────────────────────────

class FastQuotationSerializer(serializers.ModelSerializer):
    lines = FastQuotationLineNestedSerializer(many=True, required=False)

    class Meta:
        model = FastQuotation
        fields = [
            'id', 'proposal', 'name', 'description',
            'date', 'validity_date',
            'currency', 'status', 'salesperson',
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'internal_notes', 'external_notes',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'created_at', 'updated_at',
        ]

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        fast_quotation = FastQuotation.objects.create(**validated_data)

        for line_data in lines_data:
            line_data.pop('id', None)
            FastQuotationLine.objects.create(fast_quotation=fast_quotation, **line_data)

        fast_quotation.compute_totals()
        return fast_quotation

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            existing_ids = set(instance.lines.values_list('id', flat=True))
            incoming_ids = set()

            for line_data in lines_data:
                line_id = line_data.pop('id', None)
                if line_id and line_id in existing_ids:
                    FastQuotationLine.objects.filter(id=line_id, fast_quotation=instance).update(**line_data)
                    incoming_ids.add(line_id)
                else:
                    FastQuotationLine.objects.create(fast_quotation=instance, **line_data)

            to_delete = existing_ids - incoming_ids
            if to_delete:
                instance.lines.filter(id__in=to_delete).delete()

        instance.compute_totals()
        return instance


class FastQuotationReadSerializer(serializers.ModelSerializer):
    lines = FastQuotationLineSerializer(many=True, read_only=True)
    currency_display = serializers.CharField(source='currency.description', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    salesperson_display = serializers.SerializerMethodField()
    proposal_display = serializers.CharField(source='proposal.name', default=None, read_only=True)

    class Meta:
        model = FastQuotation
        fields = [
            'id', 'proposal', 'proposal_display', 'name', 'description',
            'date', 'validity_date',
            'currency', 'currency_display',
            'status', 'status_display',
            'salesperson', 'salesperson_display',
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'internal_notes', 'external_notes',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]

    def get_salesperson_display(self, obj):
        if obj.salesperson:
            full = obj.salesperson.get_full_name()
            return full if full else obj.salesperson.username
        return None


# ── FastQuotation nested (for proposal read) ───────────────────

class FastQuotationNestedReadSerializer(serializers.ModelSerializer):
    """Lightweight read serializer for quotations nested inside a proposal."""
    lines = FastQuotationLineSerializer(many=True, read_only=True)
    currency_display = serializers.CharField(source='currency.description', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FastQuotation
        fields = [
            'id', 'name', 'description',
            'date', 'validity_date',
            'currency', 'currency_display',
            'status', 'status_display',
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'internal_notes', 'external_notes',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]


# ── FastSalesProposal ──────────────────────────────────────────

class FastSalesProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FastSalesProposal
        fields = [
            'id', 'name', 'objective', 'description',
            'partner', 'partner_contact',
            'status', 'salesperson',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FastSalesProposalReadSerializer(serializers.ModelSerializer):
    quotations = FastQuotationNestedReadSerializer(many=True, read_only=True)
    partner_display = serializers.CharField(source='partner.legal_name', default=None, read_only=True)
    partner_contact_display = serializers.CharField(source='partner_contact.name', default=None, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    salesperson_display = serializers.SerializerMethodField()

    class Meta:
        model = FastSalesProposal
        fields = [
            'id', 'name', 'objective', 'description',
            'partner', 'partner_display',
            'partner_contact', 'partner_contact_display',
            'status', 'status_display',
            'salesperson', 'salesperson_display',
            'quotations',
            'is_active', 'created_at', 'updated_at',
        ]

    def get_salesperson_display(self, obj):
        if obj.salesperson:
            full = obj.salesperson.get_full_name()
            return full if full else obj.salesperson.username
        return None


# ── Convertir cotización a propuesta ───────────────────────────

class ConvertToProposalSerializer(serializers.Serializer):
    """Datos opcionales para crear la propuesta al convertir una cotización."""
    name = serializers.CharField(max_length=200, required=False, default='')
    objective = serializers.CharField(required=False, default='')
    description = serializers.CharField(required=False, default='')

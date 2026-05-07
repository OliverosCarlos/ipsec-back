from django.db import transaction
from rest_framework import serializers

from entities.serializers import (
    PartnerAddressNestedSerializer,
    PartnerContactNestedSerializer,
)
from invoicing.serializers import ClaveUnidadSerializer
from resources.serializers import ServiceVariationReadSerializer

from .models import ExternalNoteTemplate, Quotation, QuotationLine, FastSalesProposal, FastQuotation, FastQuotationLine, SalesProposal


# ── ExternalNoteTemplate ───────────────────────────────────────

class ExternalNoteTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalNoteTemplate
        fields = ['id', 'code', 'name', 'template', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── QuotationLine ──────────────────────────────────────────────

class QuotationLineSerializer(serializers.ModelSerializer):
    """Serializer for standalone QuotationLine CRUD."""
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    taxable_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    tax_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    clave_unidad_name = serializers.CharField(source='clave_unidad.name', read_only=True, default=None)

    product_service_variation_detail = ServiceVariationReadSerializer(source='product_service_variation', read_only=True)
    clave_unidad_detail = ClaveUnidadSerializer(source='clave_unidad', read_only=True)

    class Meta:
        model = QuotationLine
        fields = [
            'id', 'quotation', 'sequence',
            'product_service_variation','product_service_variation_detail',
            'description',
            'quantity', 'clave_unidad', 'clave_unidad_name', 'clave_unidad_detail',
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
            'product_service_variation', 'description',
            'quantity', 'clave_unidad', 'unit_price',
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
            'external_notes', 'internal_notes',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'number', 'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'created_at', 'updated_at',
        ]

    # ── Nested create / update ─────────────────────────────────

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        request = self.context.get('request')
        if not validated_data.get('salesperson') and request and request.user.is_authenticated:
            validated_data['salesperson'] = request.user
        quotation = Quotation.objects.create(**validated_data)

        for line_data in lines_data:
            line_data.pop('id', None)
            QuotationLine.objects.create(quotation=quotation, **line_data)

        quotation.compute_totals()
        return quotation

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        request = self.context.get('request')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.set_salesperson_from_user(request.user if request else None)
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
            'partner', 'partner_display',
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
            'internal_notes', 'external_notes',
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

    product_service_variation_detail = ServiceVariationReadSerializer(source='product_service_variation', read_only=True)
    clave_unidad_name = serializers.CharField(source='clave_unidad.name', read_only=True, default=None)

    class Meta:
        model = FastQuotationLine
        fields = [
            'id', 'fast_quotation', 'sequence',
            'product_service_variation', 'product_service_variation_detail',
            'description',
            'quantity', 'clave_unidad', 'clave_unidad_name',
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
            'product_service_variation', 'description',
            'quantity', 'clave_unidad', 'unit_price',
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

class FastQuotationProposalNestedSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    lines = FastQuotationLineNestedSerializer(many=True, required=False)

    class Meta:
        model = FastQuotation
        fields = [
            'id', 'name', 'description',
            'date', 'validity_date',
            'currency', 'status', 'salesperson',
            'internal_notes', 'external_notes',
            'lines',
            'is_active',
        ]

class FastSalesProposalSerializer(serializers.ModelSerializer):
    quotations = FastQuotationProposalNestedSerializer(many=True, required=False)

    class Meta:
        model = FastSalesProposal
        fields = [
            'id', 'name', 'objective', 'description',
            'partner', 'partner_contact',
            'status', 'salesperson',
            'quotations',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        quotations_data = validated_data.pop('quotations', [])
        proposal = FastSalesProposal.objects.create(**validated_data)

        for quotation_data in quotations_data:
            lines_data = quotation_data.pop('lines', [])
            quotation_data.pop('id', None)

            quotation = FastQuotation.objects.create(
                proposal=proposal,
                **quotation_data,
            )

            for line_data in lines_data:
                line_data.pop('id', None)
                FastQuotationLine.objects.create(
                    fast_quotation=quotation,
                    **line_data,
                )

            quotation.compute_totals()

        return proposal


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


# ── SalesProposal ──────────────────────────────────────────────

class QuotationProposalNestedSerializer(serializers.ModelSerializer):
    """Cotización resumida para anidar dentro de SalesProposal."""

    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'reference', 'date', 'validity_date',
            'status', 'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
        ]
        read_only_fields = fields


class QuotationNestedReadSerializer(serializers.ModelSerializer):
    """Lightweight read serializer for quotations nested inside a proposal."""
    lines = QuotationLineSerializer(many=True, read_only=True)
    currency_display = serializers.CharField(source='currency.description', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    partner_display = serializers.CharField(source='partner.legal_name', read_only=True)
    partner_contact_display = serializers.CharField(source='partner_contact.name', default=None, read_only=True)
    payment_method_display = serializers.CharField(source='payment_method.description', default=None, read_only=True)
    payment_form_display = serializers.CharField(source='payment_form.description', default=None, read_only=True)

    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'reference',
            'partner_display','partner_contact_display',
            'date', 'validity_date', 'expected_closing_date',
            'currency', 'currency_display', 'payment_terms_days',
            'payment_method', 'payment_method_display', 'payment_form', 'payment_form_display',
            'status', 'status_display',
            'amount_subtotal', 'amount_discount', 'amount_tax', 'amount_total',
            'internal_notes', 'external_notes',
            'lines',
            'is_active', 'created_at', 'updated_at',
        ]


class QuotationProposalWriteNestedSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    lines = QuotationLineNestedSerializer(many=True, required=False)

    class Meta:
        model = Quotation
        fields = [
            'id', 'reference',
            'partner', 'partner_contact', 'shipping_address',
            'date', 'validity_date', 'expected_closing_date',
            'currency', 'payment_terms_days',
            'payment_method', 'payment_form', 'price_list',
            'status', 'salesperson',
            'internal_notes', 'external_notes',
            'lines',
            'is_active',
        ]
        extra_kwargs = {
            'partner': {'required': False, 'allow_null': True},
            'partner_contact': {'required': False, 'allow_null': True},
            'salesperson': {'required': False, 'allow_null': True},
        }


class SalesProposalSerializer(serializers.ModelSerializer):
    quotations = QuotationProposalWriteNestedSerializer(many=True, required=False)

    @staticmethod
    def _split_number_version(number):
        base, separator, version = number.rpartition('.')
        if separator and version.isdigit():
            return base, int(version)
        return number, 1

    def _get_proposal_series(self, proposal):
        numbers = list(proposal.quotations.values_list('number', flat=True))
        if not numbers:
            return None, 0

        base, _ = self._split_number_version(numbers[0])
        max_version = 0
        for number in numbers:
            current_base, current_version = self._split_number_version(number)
            if current_base == base and current_version > max_version:
                max_version = current_version

        return base, max_version

    class Meta:
        model = SalesProposal
        fields = [
            'id', 'name', 'objective', 'description',
            'partner', 'partner_contact',
            'status', 'salesperson',
            'quotations',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        quotations_data = validated_data.pop('quotations', [])
        request = self.context.get('request')
        proposal = SalesProposal(**validated_data)
        proposal.set_salesperson_from_user(request.user if request else None)
        proposal.save()
        proposal_base_number = None
        proposal_version = 0

        for quotation_data in quotations_data:
            lines_data = quotation_data.pop('lines', [])
            quotation_data.pop('id', None)

            if not quotation_data.get('partner') and proposal.partner:
                quotation_data['partner'] = proposal.partner
            if not quotation_data.get('partner_contact') and proposal.partner_contact:
                quotation_data['partner_contact'] = proposal.partner_contact
            if not quotation_data.get('salesperson') and proposal.salesperson:
                quotation_data['salesperson'] = proposal.salesperson

            if proposal_base_number:
                proposal_version += 1
                quotation = Quotation.objects.create(
                    proposal=proposal,
                    number=f'{proposal_base_number}.{proposal_version}',
                    **quotation_data,
                )
            else:
                quotation = Quotation.objects.create(
                    proposal=proposal,
                    **quotation_data,
                )
                proposal_base_number, proposal_version = self._split_number_version(quotation.number)

            for line_data in lines_data:
                line_data.pop('id', None)
                QuotationLine.objects.create(
                    quotation=quotation,
                    **line_data,
                )

            quotation.compute_totals()

        return proposal

    @transaction.atomic
    def update(self, instance, validated_data):
        quotations_data = validated_data.pop('quotations', None)
        request = self.context.get('request')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.set_salesperson_from_user(request.user if request else None)
        instance.save()

        if quotations_data is not None:
            proposal_base_number, proposal_version = self._get_proposal_series(instance)
            existing_ids = set(instance.quotations.values_list('id', flat=True))
            incoming_ids = set()

            for quotation_data in quotations_data:
                lines_data = quotation_data.pop('lines', None)
                quotation_id = quotation_data.pop('id', None)

                if not quotation_data.get('partner') and instance.partner:
                    quotation_data['partner'] = instance.partner
                if not quotation_data.get('partner_contact') and instance.partner_contact:
                    quotation_data['partner_contact'] = instance.partner_contact
                if not quotation_data.get('salesperson') and instance.salesperson:
                    quotation_data['salesperson'] = instance.salesperson

                if quotation_id and quotation_id in existing_ids:
                    quotation = Quotation.objects.get(id=quotation_id, proposal=instance)
                    for attr, value in quotation_data.items():
                        setattr(quotation, attr, value)
                    quotation.save()

                    if lines_data is not None:
                        existing_line_ids = set(quotation.lines.values_list('id', flat=True))
                        incoming_line_ids = set()

                        for line_data in lines_data:
                            line_id = line_data.pop('id', None)
                            if line_id and line_id in existing_line_ids:
                                QuotationLine.objects.filter(id=line_id, quotation=quotation).update(**line_data)
                                incoming_line_ids.add(line_id)
                            else:
                                QuotationLine.objects.create(quotation=quotation, **line_data)

                        to_delete_lines = existing_line_ids - incoming_line_ids
                        if to_delete_lines:
                            quotation.lines.filter(id__in=to_delete_lines).delete()

                    quotation.compute_totals()
                    incoming_ids.add(quotation.id)
                else:
                    if proposal_base_number:
                        proposal_version += 1
                        quotation = Quotation.objects.create(
                            proposal=instance,
                            number=f'{proposal_base_number}.{proposal_version}',
                            **quotation_data,
                        )
                    else:
                        quotation = Quotation.objects.create(proposal=instance, **quotation_data)
                        proposal_base_number, proposal_version = self._split_number_version(quotation.number)

                    for line_data in lines_data or []:
                        line_data.pop('id', None)
                        QuotationLine.objects.create(quotation=quotation, **line_data)

                    quotation.compute_totals()
                    incoming_ids.add(quotation.id)

            to_delete = existing_ids - incoming_ids
            if to_delete:
                instance.quotations.filter(id__in=to_delete).delete()

        return instance


class SalesProposalReadSerializer(serializers.ModelSerializer):
    quotations = QuotationNestedReadSerializer(many=True, read_only=True)
    partner_display = serializers.CharField(source='partner.legal_name', default=None, read_only=True)
    partner_contact_display = serializers.CharField(source='partner_contact.name', default=None, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    salesperson_display = serializers.SerializerMethodField()

    class Meta:
        model = SalesProposal
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

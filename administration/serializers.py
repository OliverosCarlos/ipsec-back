from rest_framework import serializers
from django.db import transaction

from entities.models.catalogs import Bank, CompanySector, Country, JobPosition, PersonTitle
from invoicing.models.sat import SatCatalog
from .models import (
    Company, CompanyAddress, CompanyContact,
    CompanyBankAccount, CompanyCertificate,
)


class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAddress
        fields = '__all__'


class CompanyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyContact
        fields = '__all__'


class CompanyBankAccountSerializer(serializers.ModelSerializer):
    bank_display = serializers.SerializerMethodField()

    class Meta:
        model = CompanyBankAccount
        fields = '__all__'

    def get_bank_display(self, obj):
        return obj.bank.short_name


class CompanyCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyCertificate
        fields = [
            'id', 'company', 'serial_number',
            'cer_file', 'key_file', 'password',
            'valid_from', 'valid_to', 'is_default',
            'is_active', 'created_at', 'updated_at',
        ]
        # password se escribe pero NUNCA se devuelve
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class CompanyReadSerializer(serializers.ModelSerializer):
    addresses = CompanyAddressSerializer(many=True, read_only=True)
    contacts = CompanyContactSerializer(many=True, read_only=True)
    bank_accounts = CompanyBankAccountSerializer(many=True, read_only=True)
    tax_regime_display = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_tax_regime_display(self, obj):
        return obj.tax_regime.description


# ── Serializers anidados (sin requerir 'company') ────────────

class _NestedAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAddress
        exclude = ('company',)


class _NestedContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyContact
        exclude = ('company',)


class _NestedBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyBankAccount
        exclude = ('company',)


class _NestedCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyCertificate
        exclude = ('company',)
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CompanyFullSetupSerializer(serializers.ModelSerializer):
    """
    Crea Company y todos sus relacionados (addresses, contacts,
    bank_accounts, certificates) en una sola petición atómica.

    Nota: los archivos (logo, cer_file, key_file, photo, etc.) requieren
    multipart/form-data; con JSON puro sólo se pueden enviar los campos
    de texto/numéricos.
    """

    addresses = _NestedAddressSerializer(many=True, required=False)
    contacts = _NestedContactSerializer(many=True, required=False)
    bank_accounts = _NestedBankAccountSerializer(many=True, required=False)
    certificates = _NestedCertificateSerializer(many=True, required=False)

    class Meta:
        model = Company
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        addresses = validated_data.pop('addresses', [])
        contacts = validated_data.pop('contacts', [])
        bank_accounts = validated_data.pop('bank_accounts', [])
        certificates = validated_data.pop('certificates', [])

        company = Company.objects.create(**validated_data)

        for item in addresses:
            CompanyAddress.objects.create(company=company, **item)
        for item in contacts:
            CompanyContact.objects.create(company=company, **item)
        for item in bank_accounts:
            CompanyBankAccount.objects.create(company=company, **item)
        for item in certificates:
            CompanyCertificate.objects.create(company=company, **item)

        return company

    def to_representation(self, instance):
        return CompanyReadSerializer(instance, context=self.context).data


# ── Bulk-action item serializers ─────────────────────────────

ACTION_CHOICES = [('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted')]


class _BulkItemMixin(serializers.Serializer):
    """Base mixin: adds 'action' flag and validates id presence for update/delete."""
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        action = attrs.get('action')
        if action in ('updated', 'deleted') and not attrs.get('id'):
            raise serializers.ValidationError({'id': 'Required for action "updated" or "deleted".'})
        return attrs


class CompanyAddressBulkItemSerializer(_BulkItemMixin):
    kind = serializers.ChoiceField(choices=CompanyAddress.KIND_CHOICES, required=False)
    name = serializers.CharField(required=False, allow_blank=True, default='')
    street = serializers.CharField(required=False, allow_blank=True, default='')
    ext_no = serializers.CharField(required=False, allow_blank=True, default='')
    int_no = serializers.CharField(required=False, allow_blank=True, default='')
    neighborhood = serializers.CharField(required=False, allow_blank=True, default='')
    city = serializers.CharField(required=False, allow_blank=True, default='')
    state = serializers.CharField(required=False, allow_blank=True, default='')
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=False,
    )
    zip_code = serializers.CharField(required=False)
    is_primary = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created' and not attrs.get('zip_code'):
            raise serializers.ValidationError({'zip_code': 'Required for action "created".'})
        return attrs


class CompanyContactBulkItemSerializer(_BulkItemMixin):
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    phone_landline = serializers.CharField(required=False, allow_blank=True, default='')
    phone_landline_ext = serializers.CharField(required=False, allow_blank=True, default='')
    job_position = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(), required=False, allow_null=True,
    )
    person_title = serializers.PrimaryKeyRelatedField(
        queryset=PersonTitle.objects.all(), required=False, allow_null=True,
    )
    gender = serializers.ChoiceField(
        choices=CompanyContact.GENDER_CHOICES, required=False, default='N',
    )
    is_primary = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created' and not attrs.get('name'):
            raise serializers.ValidationError({'name': 'Required for action "created".'})
        return attrs


class CompanyBankAccountBulkItemSerializer(_BulkItemMixin):
    bank = serializers.PrimaryKeyRelatedField(queryset=Bank.objects.all(), required=False)
    account_number = serializers.CharField(required=False, allow_blank=True, default='')
    clabe = serializers.CharField(required=False)
    account_holder = serializers.CharField(required=False, allow_blank=True, default='')
    currency = serializers.PrimaryKeyRelatedField(
        queryset=SatCatalog.objects.filter(catalog='c_Moneda'),
        required=False, allow_null=True,
    )
    swift_code = serializers.CharField(required=False, allow_blank=True, default='')
    is_primary = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created':
            missing = [f for f in ('bank', 'clabe') if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {f: 'Required for action "created".' for f in missing}
                )
        return attrs


class CompanyBulkUpdateSerializer(serializers.Serializer):
    """
    Payload para actualización bulk de Company y sus relaciones.
    Los campos de la empresa son opcionales; si se envían se actualizan.
    Las listas de relaciones son opcionales; si se envían se procesan por action.
    """
    # Company fields (all optional)
    rfc = serializers.CharField(required=False)
    legal_name = serializers.CharField(required=False)
    person_type = serializers.ChoiceField(choices=Company.PERSON_TYPE, required=False)
    tax_regime = serializers.PrimaryKeyRelatedField(
        queryset=SatCatalog.objects.filter(catalog='c_RegimenFiscal'),
        required=False,
    )
    tax_zip = serializers.CharField(required=False)
    company_sector = serializers.PrimaryKeyRelatedField(
        queryset=CompanySector.objects.all(), required=False, allow_null=True,
    )
    commercial_name = serializers.CharField(required=False, allow_blank=True)
    email_billing = serializers.EmailField(required=False, allow_blank=True)
    email_contact = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=False,
    )
    slogan = serializers.CharField(required=False, allow_blank=True)
    primary_color = serializers.CharField(required=False, allow_blank=True)
    secondary_color = serializers.CharField(required=False, allow_blank=True)
    legal_representative = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    # Nested relations with action flags
    addresses = CompanyAddressBulkItemSerializer(many=True, required=False)
    contacts = CompanyContactBulkItemSerializer(many=True, required=False)
    bank_accounts = CompanyBankAccountBulkItemSerializer(many=True, required=False)


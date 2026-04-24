from rest_framework import serializers
from django.db import transaction

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


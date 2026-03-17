import json

from rest_framework import serializers

from .models import (
    Partner,
    PartnerRole,
    PartnerAddress,
    PartnerContact,
    PartnerBankAccount,
    Bank,
)
from .models.catalogs import PersonTitle, JobPosition

class PartnerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerAddress
        fields = [
            'id',
            'partner',
            'kind',
            'street',
            'ext_no',
            'int_no',
            'neighborhood',
            'city',
            'state',
            'country',
            'zip_code',
        ]
        read_only_fields = ['id']


class PartnerContactSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    job_position_display = serializers.CharField(source='job_position.name', default=None, read_only=True)
    partner_commercial_name = serializers.CharField(source='partner.commercial_name', read_only=True)

    class Meta:
        model = PartnerContact
        fields = [
            'id', 'partner', 'partner_commercial_name',
            'name', 'email', 'phone',
            'job_position', 'job_position_display',
            'gender', 'gender_display',
            'person_title', 'photo',
        ]
        read_only_fields = ['id']


class PartnerContactFullReadOnlySerializer(serializers.ModelSerializer):
    """Full read-only serializer for PartnerContact with all contact and partner details."""
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    job_position_display = serializers.CharField(source='job_position.name', default=None, read_only=True)
    person_title_display = serializers.CharField(source='person_title.abbreviation', default=None, read_only=True)

    # Partner fields
    partner_rfc = serializers.CharField(source='partner.rfc', read_only=True)
    partner_legal_name = serializers.CharField(source='partner.legal_name', read_only=True)
    partner_commercial_name = serializers.CharField(source='partner.commercial_name', read_only=True)
    partner_person_type = serializers.CharField(source='partner.person_type', read_only=True)
    partner_person_type_display = serializers.CharField(source='partner.get_person_type_display', read_only=True)
    partner_tax_regime = serializers.PrimaryKeyRelatedField(source='partner.tax_regime', read_only=True)
    partner_tax_regime_display = serializers.CharField(source='partner.tax_regime.description', default=None, read_only=True)
    partner_tax_zip = serializers.CharField(source='partner.tax_zip', read_only=True)
    partner_logo = serializers.ImageField(source='partner.logo', read_only=True)
    partner_email_billing = serializers.EmailField(source='partner.email_billing', read_only=True)
    partner_phone = serializers.CharField(source='partner.phone', read_only=True)
    partner_country = serializers.PrimaryKeyRelatedField(source='partner.country', read_only=True)
    partner_country_display = serializers.CharField(source='partner.country.name', default=None, read_only=True)
    partner_active = serializers.BooleanField(source='partner.active', read_only=True)

    class Meta:
        model = PartnerContact
        fields = [
            'id', 'partner',
            # Contact fields
            'name', 'email', 'phone',
            'job_position', 'job_position_display',
            'gender', 'gender_display',
            'person_title', 'person_title_display',
            'photo',
            # Partner fields
            'partner_rfc',
            'partner_legal_name',
            'partner_commercial_name',
            'partner_person_type',
            'partner_person_type_display',
            'partner_tax_regime',
            'partner_tax_regime_display',
            'partner_tax_zip',
            'partner_logo',
            'partner_email_billing',
            'partner_phone',
            'partner_country',
            'partner_country_display',
            'partner_active',
        ]


class PartnerRoleSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = PartnerRole
        fields = [
            'id',
            'partner',
            'role',
            'role_display',
            'diot_third_type',
            'diot_operation_type',
            'default_currency',
            'payment_terms_days',
        ]
        read_only_fields = ['id']


class PartnerAddressNestedSerializer(serializers.ModelSerializer):
    """Serializer for addresses nested inside PartnerSerializer (no partner field)."""
    class Meta:
        model = PartnerAddress
        fields = [
            'id', 'kind', 'street', 'ext_no', 'int_no',
            'neighborhood', 'city', 'state', 'country', 'zip_code',
        ]
        read_only_fields = ['id']


class PartnerContactNestedSerializer(serializers.ModelSerializer):
    """Serializer for contacts nested inside PartnerSerializer (no partner field)."""
    class Meta:
        model = PartnerContact
        fields = [
            'id', 'name', 'email', 'phone', 'job_position',
            'gender', 'person_title', 'photo',
        ]
        read_only_fields = ['id']


class PartnerRoleNestedSerializer(serializers.ModelSerializer):
    """Serializer for roles nested inside PartnerSerializer (no partner field)."""
    class Meta:
        model = PartnerRole
        fields = [
            'id', 'role', 'diot_third_type', 'diot_operation_type',
            'default_currency', 'payment_terms_days',
        ]
        read_only_fields = ['id']


class PartnerSerializer(serializers.ModelSerializer):
    addresses = PartnerAddressNestedSerializer(many=True, required=False)
    contacts = PartnerContactNestedSerializer(many=True, required=False)
    roles = PartnerRoleNestedSerializer(many=True, required=False)
    tax_regime_display = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = [
            'id',
            'rfc',
            'legal_name',
            'person_type',
            'tax_regime',
            'tax_regime_display',
            'tax_zip',
            'commercial_name',
            'logo',
            'email_billing',
            'phone',
            'country',
            'active',
            'addresses',
            'contacts',
            'roles',
        ]
        read_only_fields = ['id', 'tax_regime_display']

    def get_tax_regime_display(self, obj):
        if obj.tax_regime:
            return obj.tax_regime.description
        return None

    def to_internal_value(self, data):
        # FormData sends nested arrays as JSON strings; parse them before validation.
        mutable = {}
        for key in data:
            if hasattr(data, 'getlist'):
                values = data.getlist(key)
                mutable[key] = values if len(values) > 1 else values[0]
            else:
                mutable[key] = data[key]
        for field in ('addresses', 'contacts', 'roles'):
            raw = mutable.get(field)
            if isinstance(raw, str):
                try:
                    mutable[field] = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    pass
        return super().to_internal_value(mutable)

    def _assign_contact_photos(self, contacts, contacts_data):
        """Assign photos from request.FILES to the created contacts."""
        request = self.context.get('request')
        if not request:
            return
        for i, contact in enumerate(contacts):
            photo_key = f'contact_photo_{i}'
            photo = request.FILES.get(photo_key)
            if photo:
                contact.photo = photo
                contact.save(update_fields=['photo'])

    def create(self, validated_data):
        addresses_data = validated_data.pop('addresses', [])
        contacts_data = validated_data.pop('contacts', [])
        roles_data = validated_data.pop('roles', [])

        request = self.context.get('request')
        logo = request.FILES.get('logo') if request else None
        if logo:
            validated_data['logo'] = logo

        partner = Partner.objects.create(**validated_data)

        for addr in addresses_data:
            PartnerAddress.objects.create(partner=partner, **addr)

        created_contacts = []
        for contact in contacts_data:
            contact.pop('photo', None)
            created_contacts.append(
                PartnerContact.objects.create(partner=partner, **contact)
            )
        self._assign_contact_photos(created_contacts, contacts_data)

        for role in roles_data:
            PartnerRole.objects.create(partner=partner, **role)

        return partner

    def update(self, instance, validated_data):
        addresses_data = validated_data.pop('addresses', None)
        contacts_data = validated_data.pop('contacts', None)
        roles_data = validated_data.pop('roles', None)

        request = self.context.get('request')
        logo = request.FILES.get('logo') if request else None
        if logo:
            validated_data['logo'] = logo

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if addresses_data is not None:
            instance.addresses.all().delete()
            for addr in addresses_data:
                PartnerAddress.objects.create(partner=instance, **addr)

        if contacts_data is not None:
            instance.contacts.all().delete()
            created_contacts = []
            for contact in contacts_data:
                contact.pop('photo', None)
                created_contacts.append(
                    PartnerContact.objects.create(partner=instance, **contact)
                )
            self._assign_contact_photos(created_contacts, contacts_data)

        if roles_data is not None:
            instance.roles.all().delete()
            for role in roles_data:
                PartnerRole.objects.create(partner=instance, **role)

        return instance


class PartnerContactReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for contacts with display values."""
    job_position_display = serializers.CharField(source='job_position.name', default=None, read_only=True)
    person_title_display = serializers.CharField(source='person_title.abbreviation', default=None, read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = PartnerContact
        fields = [
            'id', 'name', 'email', 'phone', 'job_position', 'job_position_display',
            'gender', 'gender_display', 'person_title', 'person_title_display', 'photo',
        ]


class PartnerRoleReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for roles with display values."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    diot_third_type_display = serializers.CharField(source='diot_third_type.description', default=None, read_only=True)
    diot_operation_type_display = serializers.CharField(source='diot_operation_type.description', default=None, read_only=True)
    default_currency_display = serializers.CharField(source='default_currency.description', default=None, read_only=True)

    class Meta:
        model = PartnerRole
        fields = [
            'id', 'role', 'role_display',
            'diot_third_type', 'diot_third_type_display',
            'diot_operation_type', 'diot_operation_type_display',
            'default_currency', 'default_currency_display',
            'payment_terms_days',
        ]


class PartnerAddressReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for addresses with display values."""
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    country_display = serializers.CharField(source='country.name', default=None, read_only=True)

    class Meta:
        model = PartnerAddress
        fields = [
            'id', 'kind', 'kind_display', 'street', 'ext_no', 'int_no',
            'neighborhood', 'city', 'state', 'country', 'country_display', 'zip_code',
        ]


class PartnerReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for Partner with nested display values."""
    addresses = PartnerAddressReadSerializer(many=True, read_only=True)
    contacts = PartnerContactReadSerializer(many=True, read_only=True)
    roles = PartnerRoleReadSerializer(many=True, read_only=True)
    tax_regime_display = serializers.SerializerMethodField()
    person_type_display = serializers.CharField(source='get_person_type_display', read_only=True)
    country_display = serializers.CharField(source='country.name', default=None, read_only=True)

    class Meta:
        model = Partner
        fields = [
            'id',
            'rfc',
            'legal_name',
            'person_type',
            'person_type_display',
            'tax_regime',
            'tax_regime_display',
            'tax_zip',
            'commercial_name',
            'logo',
            'email_billing',
            'phone',
            'country',
            'country_display',
            'active',
            'addresses',
            'contacts',
            'roles',
        ]

    def get_tax_regime_display(self, obj):
        if obj.tax_regime:
            return obj.tax_regime.description
        return None


class PartnerBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerBankAccount
        fields = ['id', 'partner', 'bank', 'clabe', 'account_name']
        read_only_fields = ['id']


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            'id',
            'code',
            'short_name',
            'legal_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PersonTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonTitle
        fields = [
            'id',
            'code',
            'name',
            'abbreviation',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosition
        fields = [
            'id',
            'code',
            'name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

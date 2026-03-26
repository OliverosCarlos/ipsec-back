import json
import unicodedata
from datetime import date

from rest_framework import serializers

from core.models import Account
from .models import (
    Partner,
    PartnerRole,
    PartnerAddress,
    PartnerContact,
    PartnerBankAccount,
    Bank,
    Department,
    EmployeeStatus,
    Employee,
)
from .models.catalogs import PersonTitle, JobPosition, CompanySector, Country
from invoicing.models.sat import SatCatalog

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
            'phone_landline', 'phone_landline_ext',
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
            'phone_landline', 'phone_landline_ext',
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


# ── Bulk-action item serializers ─────────────────────────

ACTION_CHOICES = [('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted')]


class _BulkItemMixin(serializers.Serializer):
    """Base mixin: adds 'action' flag and validates id presence for update/delete."""
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        action = attrs.get('action')
        if action in ('updated', 'deleted') and not attrs.get('id'):
            raise serializers.ValidationError({'id': 'Required for action "updated" or "deleted".'})
        return attrs


class PartnerRoleBulkItemSerializer(_BulkItemMixin):
    role = serializers.ChoiceField(choices=PartnerRole.ROLE_CHOICES, required=False)
    diot_third_type = serializers.PrimaryKeyRelatedField(
        queryset=SatCatalog.objects.filter(catalog='DIOT_TipoTercero'),
        required=False, allow_null=True,
    )
    diot_operation_type = serializers.PrimaryKeyRelatedField(
        queryset=SatCatalog.objects.filter(catalog='DIOT_TipoOperacion'),
        required=False, allow_null=True,
    )
    default_currency = serializers.PrimaryKeyRelatedField(
        queryset=SatCatalog.objects.filter(catalog='c_Moneda'),
        required=False, allow_null=True,
    )
    payment_terms_days = serializers.IntegerField(required=False, default=0)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] in ('created', 'updated') and not attrs.get('role'):
            raise serializers.ValidationError({'role': 'Required for action "created" or "updated".'})
        return attrs


class PartnerAddressBulkItemSerializer(_BulkItemMixin):
    kind = serializers.ChoiceField(choices=PartnerAddress.KIND_CHOICES, required=False)
    street = serializers.CharField(required=False, allow_blank=True, default='')
    ext_no = serializers.CharField(required=False, allow_blank=True, default='')
    int_no = serializers.CharField(required=False, allow_blank=True, default='')
    neighborhood = serializers.CharField(required=False, allow_blank=True, default='')
    city = serializers.CharField(required=False, allow_blank=True, default='')
    state = serializers.CharField(required=False, allow_blank=True, default='')
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
    )
    zip_code = serializers.CharField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created' and not attrs.get('zip_code'):
            raise serializers.ValidationError({'zip_code': 'Required for action "created".'})
        return attrs


class PartnerContactBulkItemSerializer(_BulkItemMixin):
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    phone_landline = serializers.CharField(required=False, allow_blank=True, default='')
    phone_landline_ext = serializers.CharField(required=False, allow_blank=True, default='')
    job_position = serializers.PrimaryKeyRelatedField(
        queryset=JobPosition.objects.all(), required=False, allow_null=True,
    )
    gender = serializers.ChoiceField(choices=PartnerContact.GENDER_CHOICES, required=False, default='N')
    person_title = serializers.PrimaryKeyRelatedField(
        queryset=PersonTitle.objects.all(), required=False, allow_null=True,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['action'] == 'created' and not attrs.get('name'):
            raise serializers.ValidationError({'name': 'Required for action "created".'})
        return attrs


class PartnerBulkUpdateSerializer(serializers.Serializer):
    """
    Payload para actualización bulk de Partner y sus relaciones.
    Los campos del partner son opcionales; si se envían se actualizan.
    Las listas de relaciones son opcionales; si se envían se procesan por action.
    """
    # Partner fields (all optional)
    rfc = serializers.CharField(required=False)
    legal_name = serializers.CharField(required=False)
    person_type = serializers.ChoiceField(choices=Partner.PERSON_TYPE, required=False)
    tax_regime = serializers.PrimaryKeyRelatedField(
        queryset=SatCatalog.objects.filter(catalog='c_RegimenFiscal'),
        required=False,
    )
    tax_zip = serializers.CharField(required=False)
    commercial_name = serializers.CharField(required=False, allow_blank=True)
    email_billing = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=False,
    )
    active = serializers.BooleanField(required=False)
    sector = serializers.ChoiceField(choices=Partner.SECTOR_CHOICES, required=False, allow_blank=True)
    company_sector = serializers.PrimaryKeyRelatedField(
        queryset=CompanySector.objects.all(), required=False, allow_null=True,
    )

    # Nested relations with action flags
    roles = PartnerRoleBulkItemSerializer(many=True, required=False)
    addresses = PartnerAddressBulkItemSerializer(many=True, required=False)
    contacts = PartnerContactBulkItemSerializer(many=True, required=False)


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
            'id', 'name', 'email', 'phone',
            'phone_landline', 'phone_landline_ext',
            'job_position',
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
            'sector',
            'company_sector'
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
            'id', 'name', 'email', 'phone',
            'phone_landline', 'phone_landline_ext',
            'job_position', 'job_position_display',
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
    sector_display = serializers.CharField(source='get_sector_display', read_only=True)
    company_sector_display = serializers.CharField(source='company_sector.name', default=None, read_only=True)

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
            'sector',
            'sector_display',
            'company_sector',
            'company_sector_display',
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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            'id',
            'code',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySector
        fields = [
            'id',
            'code',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeStatus
        fields = [
            'id',
            'code',
            'name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name',
            'last_name_father',
            'last_name_mother',
            'date_of_birth',
            'age',
            'gender',
            'email',
            'phone',
            'photo',
            'department',
            'job_position',
            'status',
            'account',
            'full_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'account', 'created_at', 'updated_at']

    @staticmethod
    def _normalize(text):
        """Remove accents and convert to lowercase ASCII."""
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower()

    def _build_username(self, first_name, last_name_father, last_name_mother):
        """Generate a unique username: first_name.last_father.last_mother"""
        parts = [
            self._normalize(first_name),
            self._normalize(last_name_father),
        ]
        if last_name_mother:
            parts.append(self._normalize(last_name_mother))
        base = '.'.join(parts)
        username = base
        counter = 1
        while Account.objects.filter(username=username).exists():
            username = f'{base}{counter}'
            counter += 1
        return username

    def create(self, validated_data):
        validated_data.pop('account', None)
        first_name = validated_data['first_name']
        last_name_father = validated_data['last_name_father']
        last_name_mother = validated_data.get('last_name_mother', '')

        username = self._build_username(first_name, last_name_father, last_name_mother)
        default_password = f'Tepic{date.today().year}'

        account = Account.objects.create_user(
            username=username,
            password=default_password,
            email=validated_data.get('email', ''),
            first_name=first_name,
            last_name=last_name_father,
        )
        validated_data['account'] = account
        return super().create(validated_data)


class EmployeeReadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    department_display = serializers.CharField(source='department.name', default=None, read_only=True)
    job_position_display = serializers.CharField(source='job_position.name', default=None, read_only=True)
    status_display = serializers.CharField(source='status.name', default=None, read_only=True)
    account_display = serializers.CharField(source='account.username', default=None, read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'first_name',
            'last_name_father',
            'last_name_mother',
            'date_of_birth',
            'age',
            'gender',
            'gender_display',
            'email',
            'phone',
            'photo',
            'department',
            'department_display',
            'job_position',
            'job_position_display',
            'status',
            'status_display',
            'account',
            'account_display',
            'full_name',
            'is_active',
            'created_at',
            'updated_at',
        ]

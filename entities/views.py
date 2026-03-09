from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import (
	Partner,
	PartnerRole,
	PartnerAddress,
	PartnerContact,
	PartnerBankAccount,
    Bank,
)
from .models.catalogs import PersonTitle, JobPosition
from .serializers import (
	PartnerSerializer,
	PartnerReadSerializer,
	PartnerRoleSerializer,
	PartnerAddressSerializer,
	PartnerContactSerializer,
	PartnerContactFullReadOnlySerializer,
	PartnerBankAccountSerializer,
    BankSerializer,
	PersonTitleSerializer,
	JobPositionSerializer,
)


# ── Partner ──────────────────────────────────────────────

class PartnerListCreateView(generics.ListCreateAPIView):
	queryset = Partner.objects.select_related('tax_regime', 'country')
	parser_classes = [MultiPartParser, FormParser, JSONParser]
	search_fields = ['rfc', 'legal_name', 'commercial_name', 'email_billing']
	filterset_fields = ['active', 'person_type', 'tax_regime', 'country']

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return PartnerReadSerializer
		return PartnerSerializer


class PartnerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Partner.objects.select_related('tax_regime', 'country')
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return PartnerReadSerializer
		return PartnerSerializer


# ── PartnerRole ──────────────────────────────────────────

class PartnerRoleListCreateView(generics.ListCreateAPIView):
	queryset = PartnerRole.objects.select_related(
		'partner',
		'diot_third_type',
		'diot_operation_type',
		'default_currency',
	)
	serializer_class = PartnerRoleSerializer
	filterset_fields = ['partner', 'role', 'diot_third_type', 'diot_operation_type', 'default_currency']


class PartnerRoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PartnerRole.objects.select_related(
		'partner',
		'diot_third_type',
		'diot_operation_type',
		'default_currency',
	)
	serializer_class = PartnerRoleSerializer


# ── PartnerAddress ───────────────────────────────────────

class PartnerAddressListCreateView(generics.ListCreateAPIView):
	queryset = PartnerAddress.objects.select_related('partner', 'country')
	serializer_class = PartnerAddressSerializer
	filterset_fields = ['partner', 'kind', 'country']


class PartnerAddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PartnerAddress.objects.select_related('partner', 'country')
	serializer_class = PartnerAddressSerializer


# ── PartnerContact ───────────────────────────────────────

class PartnerContactListCreateView(generics.ListCreateAPIView):
	queryset = PartnerContact.objects.select_related('partner')
	serializer_class = PartnerContactSerializer
	search_fields = ['name', 'email', 'phone', 'job_position__name']
	filterset_fields = ['partner']


class PartnerContactRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PartnerContact.objects.select_related('partner')
	serializer_class = PartnerContactSerializer


class PartnerContactFullRetrieveView(generics.RetrieveAPIView):
	queryset = PartnerContact.objects.select_related(
		'partner', 'partner__tax_regime', 'partner__country',
		'job_position', 'person_title',
	)
	serializer_class = PartnerContactFullReadOnlySerializer


# ── PartnerBankAccount ───────────────────────────────────

class PartnerBankAccountListCreateView(generics.ListCreateAPIView):
	queryset = PartnerBankAccount.objects.select_related('partner', 'bank')
	serializer_class = PartnerBankAccountSerializer
	search_fields = ['clabe', 'account_name']
	filterset_fields = ['partner', 'bank']


class PartnerBankAccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PartnerBankAccount.objects.select_related('partner', 'bank')
	serializer_class = PartnerBankAccountSerializer


# ── Bank ─────────────────────────────────────────────────

class BankListCreateView(generics.ListCreateAPIView):
	queryset = Bank.objects.all()
	serializer_class = BankSerializer
	search_fields = ['code', 'short_name', 'legal_name']
	filterset_fields = ['is_active']


class BankRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Bank.objects.all()
	serializer_class = BankSerializer


# ── PersonTitle ───────────────────────────────────────────

class PersonTitleListCreateView(generics.ListCreateAPIView):
	queryset = PersonTitle.objects.all()
	serializer_class = PersonTitleSerializer
	search_fields = ['code', 'name']
	filterset_fields = ['is_active']


class PersonTitleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PersonTitle.objects.all()
	serializer_class = PersonTitleSerializer


# ── JobPosition ───────────────────────────────────────────

class JobPositionListCreateView(generics.ListCreateAPIView):
	queryset = JobPosition.objects.all()
	serializer_class = JobPositionSerializer
	search_fields = ['code', 'name']
	filterset_fields = ['is_active']


class JobPositionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = JobPosition.objects.all()
	serializer_class = JobPositionSerializer


from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Prefetch

from .filters import PartnerFilter
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
from .serializers import (
	PartnerSerializer,
	PartnerReadSerializer,
	PartnerRoleSerializer,
	PartnerBulkUpdateSerializer,
	PartnerAddressSerializer,
	PartnerContactSerializer,
	PartnerContactFullReadOnlySerializer,
	PartnerBankAccountSerializer,
    BankSerializer,
	PersonTitleSerializer,
	JobPositionSerializer,
	DepartmentSerializer,
	EmployeeStatusSerializer,
	CompanySectorSerializer,
	EmployeeSerializer,
	EmployeeReadSerializer,
	PartnerDashboardSerializer,
)


# ── Partner ──────────────────────────────────────────────

class PartnerListCreateView(generics.ListCreateAPIView):
	parser_classes = [MultiPartParser, FormParser, JSONParser]
	search_fields = ['rfc', 'legal_name', 'commercial_name', 'email_billing']
	filterset_class = PartnerFilter

	def get_queryset(self):
		"""Optimize queryset with prefetch_related for nested serializers."""
		# Prefetch addresses with their related countries
		addresses_qs = PartnerAddress.objects.select_related('country')
		address_prefetch = Prefetch('addresses', queryset=addresses_qs)
		
		# Prefetch contacts with their related job_position and person_title
		contacts_qs = PartnerContact.objects.select_related('job_position', 'person_title')
		contact_prefetch = Prefetch('contacts', queryset=contacts_qs)
		
		# Prefetch roles with their related SatCatalog fields
		roles_qs = PartnerRole.objects.select_related(
			'diot_third_type', 'diot_operation_type', 'default_currency'
		)
		role_prefetch = Prefetch('roles', queryset=roles_qs)
		
		return Partner.objects.select_related(
			'tax_regime', 'country', 'company_sector'
		).prefetch_related(
			address_prefetch, contact_prefetch, role_prefetch
		)

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return PartnerReadSerializer
		return PartnerSerializer


class PartnerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def get_queryset(self):
		"""Optimize queryset with prefetch_related for nested serializers."""
		# Prefetch addresses with their related countries
		addresses_qs = PartnerAddress.objects.select_related('country')
		address_prefetch = Prefetch('addresses', queryset=addresses_qs)
		
		# Prefetch contacts with their related job_position and person_title
		contacts_qs = PartnerContact.objects.select_related('job_position', 'person_title')
		contact_prefetch = Prefetch('contacts', queryset=contacts_qs)
		
		# Prefetch roles with their related SatCatalog fields
		roles_qs = PartnerRole.objects.select_related(
			'diot_third_type', 'diot_operation_type', 'default_currency'
		)
		role_prefetch = Prefetch('roles', queryset=roles_qs)
		
		return Partner.objects.select_related(
			'tax_regime', 'country', 'company_sector'
		).prefetch_related(
			address_prefetch, contact_prefetch, role_prefetch
		)

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


class PartnerBulkUpdateView(APIView):
	"""
	Actualización integral de un Partner y sus relaciones (roles, addresses, contacts).
	Cada relación envía una lista con un campo 'action': created, updated o deleted.

	PUT /partners/<pk>/bulk-update/
	{
	    "legal_name": "Nuevo nombre",
	    "roles": [
	        {"action": "created", "role": "CUSTOMER", ...},
	        {"action": "updated", "id": 5, "role": "SUPPLIER", ...},
	        {"action": "deleted", "id": 3}
	    ],
	    "addresses": [...],
	    "contacts": [...]
	}
	"""
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def put(self, request, pk):
		from django.db import transaction

		try:
			partner = Partner.objects.get(pk=pk)
		except Partner.DoesNotExist:
			return Response({'detail': 'Partner not found.'}, status=status.HTTP_404_NOT_FOUND)

		serializer = PartnerBulkUpdateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data

		# Separate partner fields from relation lists
		roles_data = data.pop('roles', None)
		addresses_data = data.pop('addresses', None)
		contacts_data = data.pop('contacts', None)
		partner_fields = data  # remaining keys are partner-level fields

		result = {'partner_updated': False, 'roles': {}, 'addresses': {}, 'contacts': {}}

		with transaction.atomic():
			# ── Update Partner fields ──
			if partner_fields:
				# Handle logo from FILES separately
				logo = request.FILES.get('logo')
				if logo:
					partner_fields['logo'] = logo
				for attr, value in partner_fields.items():
					setattr(partner, attr, value)
				partner.save()
				result['partner_updated'] = True

			# ── Process roles ──
			if roles_data is not None:
				result['roles'] = self._process_relations(
					PartnerRole, partner, roles_data,
				)

			# ── Process addresses ──
			if addresses_data is not None:
				result['addresses'] = self._process_relations(
					PartnerAddress, partner, addresses_data,
				)

			# ── Process contacts ──
			if contacts_data is not None:
				result['contacts'] = self._process_relations(
					PartnerContact, partner, contacts_data,
				)

		return Response(result, status=status.HTTP_200_OK)

	@staticmethod
	def _process_relations(model_class, partner, items_data):
		"""Generic handler for create/update/delete on a related model."""
		created = []
		updated = []
		deleted = []

		for item in items_data:
			action = item.pop('action')
			item_id = item.pop('id', None)

			if action == 'created':
				obj = model_class.objects.create(partner=partner, **item)
				created.append(obj.id)

			elif action == 'updated':
				model_class.objects.filter(id=item_id, partner=partner).update(**item)
				updated.append(item_id)

			elif action == 'deleted':
				model_class.objects.filter(id=item_id, partner=partner).delete()
				deleted.append(item_id)

		return {'created': created, 'updated': updated, 'deleted': deleted}


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


# ── Department ────────────────────────────────────────────

class DepartmentListCreateView(generics.ListCreateAPIView):
	queryset = Department.objects.all()
	serializer_class = DepartmentSerializer
	search_fields = ['code', 'name']
	filterset_fields = ['is_active']


class DepartmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Department.objects.all()
	serializer_class = DepartmentSerializer


# ── EmployeeStatus ────────────────────────────────────────

class EmployeeStatusListCreateView(generics.ListCreateAPIView):
	queryset = EmployeeStatus.objects.all()
	serializer_class = EmployeeStatusSerializer
	search_fields = ['code', 'name']
	filterset_fields = ['is_active']


class EmployeeStatusRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = EmployeeStatus.objects.all()
	serializer_class = EmployeeStatusSerializer


# ── CompanySector ─────────────────────────────────────────

class CompanySectorPagination(PageNumberPagination):
	page_size = 100
	page_size_query_param = 'page_size'
	max_page_size = 100


class CompanySectorListCreateView(generics.ListCreateAPIView):
	queryset = CompanySector.objects.all()
	serializer_class = CompanySectorSerializer
	pagination_class = CompanySectorPagination
	search_fields = ['code', 'name']
	filterset_fields = ['is_active']


class CompanySectorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = CompanySector.objects.all()
	serializer_class = CompanySectorSerializer


# ── Employee ──────────────────────────────────────────────


class EmployeeListCreateView(generics.ListCreateAPIView):
	queryset = Employee.objects.select_related('department', 'job_position', 'status', 'account')
	parser_classes = [MultiPartParser, FormParser, JSONParser]
	search_fields = ['first_name', 'last_name_father', 'last_name_mother', 'email']
	filterset_fields = ['is_active', 'department', 'job_position', 'status']

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return EmployeeReadSerializer
		return EmployeeSerializer


class EmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Employee.objects.select_related('department', 'job_position', 'status', 'account')
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return EmployeeReadSerializer
		return EmployeeSerializer


# ── Partner Dashboard ─────────────────────────────────────

class PartnerDashboardView(APIView):
	def get(self, request):
		from django.db.models import Count, Q

		data = Partner.objects.aggregate(
			total_partners=Count('id'),
			total_customers=Count('id', filter=Q(roles__role='CUSTOMER'), distinct=True),
			total_suppliers=Count('id', filter=Q(roles__role='SUPPLIER'), distinct=True),
			total_private_sector=Count('id', filter=Q(sector='PRIVATE')),
		)

		serializer = PartnerDashboardSerializer(data)
		return Response(serializer.data)


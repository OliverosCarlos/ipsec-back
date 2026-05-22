from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Company, CompanyAddress, CompanyContact,
    CompanyBankAccount, CompanyCertificate,
)
from .serializers import (
    CompanyAddressSerializer, CompanyBankAccountSerializer,
    CompanyBulkUpdateSerializer,
    CompanyCertificateSerializer, CompanyContactSerializer,
    CompanyFullSetupSerializer, CompanyReadSerializer, CompanySerializer,
)


# ── Company ───────────────────────────────────────────────

class CompanyListCreateView(generics.ListCreateAPIView):
    """
    GET    /api/administration/company/   → lista de empresas
    POST   /api/administration/company/   → crear empresa
    """

    queryset = Company.objects.select_related(
        'tax_regime', 'country', 'company_sector'
    ).prefetch_related('addresses', 'contacts', 'bank_accounts')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CompanyReadSerializer
        return CompanySerializer

    def create(self, request, *args, **kwargs):
        if Company.objects.exists():
            return Response(
                {'detail': 'Ya existe una empresa registrada. Use PUT/PATCH.'},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class CompanyDetailView(APIView):
    """
    GET    /api/administration/company/<pk>/   → datos de la primera empresa (singleton)
    PUT    /api/administration/company/<pk>/   → actualizar
    PATCH  /api/administration/company/<pk>/   → actualización parcial
    """

    def _get_instance(self):
        return Company.objects.first()

    def get(self, request, pk=None):
        instance = self._get_instance()
        if instance is None:
            return Response(
                {'detail': 'Aún no se ha registrado la empresa.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CompanyReadSerializer(instance).data)

    def put(self, request, pk=None):
        return self._update(request, partial=False)

    def patch(self, request, pk=None):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        instance = self._get_instance()
        if instance is None:
            return Response(
                {'detail': 'No existe una empresa para actualizar.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── CompanyAddress ──────────────────────────────────────────

class CompanyAddressListCreateView(generics.ListCreateAPIView):
    queryset = CompanyAddress.objects.select_related('company', 'country')
    serializer_class = CompanyAddressSerializer
    filterset_fields = ['kind', 'is_primary', 'is_active']


class CompanyAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyAddress.objects.select_related('company', 'country')
    serializer_class = CompanyAddressSerializer


# ── CompanyContact ──────────────────────────────────────────

class CompanyContactListCreateView(generics.ListCreateAPIView):
    queryset = CompanyContact.objects.select_related(
        'company', 'job_position', 'person_title',
    )
    serializer_class = CompanyContactSerializer
    filterset_fields = ['is_primary', 'is_active']
    search_fields = ['name', 'email']


class CompanyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyContact.objects.select_related(
        'company', 'job_position', 'person_title',
    )
    serializer_class = CompanyContactSerializer


# ── CompanyBankAccount ──────────────────────────────────────

class CompanyBankAccountListCreateView(generics.ListCreateAPIView):
    queryset = CompanyBankAccount.objects.select_related(
        'company', 'bank', 'currency',
    )
    serializer_class = CompanyBankAccountSerializer
    filterset_fields = ['bank', 'is_primary', 'is_active']


class CompanyBankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyBankAccount.objects.select_related(
        'company', 'bank', 'currency',
    )
    serializer_class = CompanyBankAccountSerializer


# ── CompanyCertificate ──────────────────────────────────────

class CompanyCertificateListCreateView(generics.ListCreateAPIView):
    queryset = CompanyCertificate.objects.select_related('company')
    serializer_class = CompanyCertificateSerializer
    filterset_fields = ['is_default', 'is_active']


class CompanyCertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyCertificate.objects.select_related('company')
    serializer_class = CompanyCertificateSerializer


# ── Setup completo (Company + relacionados) ─────────────────

class CompanyFullSetupView(APIView):
    """
    POST /api/administration/company/setup/

    Crea Company junto con sus addresses, contacts, bank_accounts
    y certificates en una sola petición atómica.
    """

    def post(self, request):
        if Company.objects.exists():
            return Response(
                {'detail': 'Ya existe una empresa registrada. Use PUT/PATCH sobre /company/.'},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = CompanyFullSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return Response(
            CompanyReadSerializer(company).data,
            status=status.HTTP_201_CREATED,
        )


# ── Bulk update Company + relaciones ────────────────────────

class CompanyBulkUpdateView(APIView):
    """
    Actualización integral de Company y sus relaciones
    (addresses, contacts, bank_accounts).

    Cada relación envía una lista con un campo 'action': created, updated o deleted.

    PUT /api/administration/company/<uuid:pk>/bulk-update/
    {
        "legal_name": "Nuevo nombre",
        "addresses": [
            {"action": "created", "kind": "FISCAL", "zip_code": "01000", ...},
            {"action": "updated", "id": "<uuid>", "city": "CDMX", ...},
            {"action": "deleted", "id": "<uuid>"}
        ],
        "contacts": [...],
        "bank_accounts": [...]
    }
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request, pk):
        from django.db import transaction

        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({'detail': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanyBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Separate company fields from relation lists
        addresses_data = data.pop('addresses', None)
        contacts_data = data.pop('contacts', None)
        bank_accounts_data = data.pop('bank_accounts', None)
        company_fields = data  # remaining keys are company-level fields

        result = {
            'company_updated': False,
            'addresses': {},
            'contacts': {},
            'bank_accounts': {},
        }

        with transaction.atomic():
            # ── Update Company fields ──
            if company_fields or request.FILES:
                # Handle uploaded files (logo, logo_dark) separately
                for file_field in ('logo', 'logo_dark'):
                    uploaded = request.FILES.get(file_field)
                    if uploaded:
                        company_fields[file_field] = uploaded
                if company_fields:
                    for attr, value in company_fields.items():
                        setattr(company, attr, value)
                    company.save()
                    result['company_updated'] = True

            # ── Process addresses ──
            if addresses_data is not None:
                result['addresses'] = self._process_relations(
                    CompanyAddress, company, addresses_data,
                )

            # ── Process contacts ──
            if contacts_data is not None:
                result['contacts'] = self._process_relations(
                    CompanyContact, company, contacts_data,
                )

            # ── Process bank accounts ──
            if bank_accounts_data is not None:
                result['bank_accounts'] = self._process_relations(
                    CompanyBankAccount, company, bank_accounts_data,
                )

        return Response(result, status=status.HTTP_200_OK)

    @staticmethod
    def _process_relations(model_class, company, items_data):
        """Generic handler for create/update/delete on a related model."""
        created = []
        updated = []
        deleted = []

        for item in items_data:
            action = item.pop('action')
            item_id = item.pop('id', None)

            if action == 'created':
                obj = model_class.objects.create(company=company, **item)
                created.append(str(obj.id))

            elif action == 'updated':
                model_class.objects.filter(id=item_id, company=company).update(**item)
                updated.append(str(item_id))

            elif action == 'deleted':
                model_class.objects.filter(id=item_id, company=company).delete()
                deleted.append(str(item_id))

        return {'created': created, 'updated': updated, 'deleted': deleted}

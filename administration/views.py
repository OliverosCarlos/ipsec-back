from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Company, CompanyAddress, CompanyContact,
    CompanyBankAccount, CompanyCertificate,
)
from .serializers import (
    CompanyAddressSerializer, CompanyBankAccountSerializer,
    CompanyCertificateSerializer, CompanyContactSerializer,
    CompanyFullSetupSerializer, CompanyReadSerializer, CompanySerializer,
)


# ── Company (Singleton) ─────────────────────────────────────

class CompanyView(APIView):
    """
    GET    /api/administration/company/   → datos de la empresa
    POST   /api/administration/company/   → crear (solo si no existe)
    PUT    /api/administration/company/   → actualizar la única instancia
    PATCH  /api/administration/company/   → actualización parcial
    """

    def get(self, request):
        instance = Company.objects.first()
        if instance is None:
            return Response(
                {'detail': 'Aún no se ha registrado la empresa.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CompanyReadSerializer(instance).data)

    def post(self, request):
        if Company.objects.exists():
            return Response(
                {'detail': 'Ya existe una empresa registrada. Use PUT/PATCH.'},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = CompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        return self._update(request, partial=False)

    def patch(self, request):
        return self._update(request, partial=True)

    def _update(self, request, partial):
        instance = Company.objects.first()
        if instance is None:
            return Response(
                {'detail': 'No existe una empresa para actualizar.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CompanySerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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

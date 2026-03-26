from rest_framework import generics

from .models import Quotation, QuotationLine, FastSalesProposal, FastQuotation, FastQuotationLine
from .serializers import (
    QuotationLineSerializer,
    QuotationReadSerializer,
    QuotationSerializer,
    FastQuotationLineSerializer,
    FastQuotationReadSerializer,
    FastQuotationSerializer,
    FastSalesProposalReadSerializer,
    FastSalesProposalSerializer,
)


# ── Quotation ──────────────────────────────────────────────────

class QuotationListCreateView(generics.ListCreateAPIView):
    queryset = Quotation.objects.select_related(
        'partner', 'partner_contact', 'shipping_address',
        'currency', 'payment_method', 'payment_form',
        'price_list', 'salesperson',
    ).prefetch_related('lines__product_variation', 'lines__unit_of_measure')
    search_fields = ['number', 'reference', 'partner__legal_name', 'partner__rfc']
    filterset_fields = ['status', 'partner', 'currency', 'salesperson', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuotationReadSerializer
        return QuotationSerializer


class QuotationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quotation.objects.select_related(
        'partner', 'partner_contact', 'shipping_address',
        'currency', 'payment_method', 'payment_form',
        'price_list', 'salesperson',
    ).prefetch_related('lines__product_variation', 'lines__unit_of_measure')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuotationReadSerializer
        return QuotationSerializer


# ── QuotationLine (standalone CRUD) ───────────────────────────

class QuotationLineListCreateView(generics.ListCreateAPIView):
    queryset = QuotationLine.objects.select_related(
        'quotation', 'product_variation', 'unit_of_measure',
    )
    serializer_class = QuotationLineSerializer
    filterset_fields = ['quotation', 'product_variation', 'is_active']


class QuotationLineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuotationLine.objects.select_related(
        'quotation', 'product_variation', 'unit_of_measure',
    )
    serializer_class = QuotationLineSerializer


# ── FastQuotation ──────────────────────────────────────────────

class FastQuotationListCreateView(generics.ListCreateAPIView):
    queryset = FastQuotation.objects.select_related(
        'proposal', 'currency', 'salesperson',
    ).prefetch_related('lines__product_variation', 'lines__unit_of_measure')
    search_fields = ['partner_name', 'subject', 'proposal__name']
    filterset_fields = ['status', 'proposal', 'currency', 'salesperson', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FastQuotationReadSerializer
        return FastQuotationSerializer


class FastQuotationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FastQuotation.objects.select_related(
        'proposal', 'currency', 'salesperson',
    ).prefetch_related('lines__product_variation', 'lines__unit_of_measure')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FastQuotationReadSerializer
        return FastQuotationSerializer


# ── FastQuotationLine (standalone CRUD) ────────────────────────

class FastQuotationLineListCreateView(generics.ListCreateAPIView):
    queryset = FastQuotationLine.objects.select_related(
        'fast_quotation', 'product_variation', 'unit_of_measure',
    )
    serializer_class = FastQuotationLineSerializer
    filterset_fields = ['fast_quotation', 'product_variation', 'is_active']


class FastQuotationLineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FastQuotationLine.objects.select_related(
        'fast_quotation', 'product_variation', 'unit_of_measure',
    )
    serializer_class = FastQuotationLineSerializer


# ── FastSalesProposal ────────────────────────────────────────

class FastSalesProposalListCreateView(generics.ListCreateAPIView):
    queryset = FastSalesProposal.objects.select_related(
        'partner', 'partner_contact', 'salesperson',
    ).prefetch_related(
        'quotations__lines__product_variation',
        'quotations__lines__unit_of_measure',
        'quotations__currency',
    )
    search_fields = ['name', 'objective', 'partner__legal_name']
    filterset_fields = ['status', 'partner', 'salesperson', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FastSalesProposalReadSerializer
        return FastSalesProposalSerializer


class FastSalesProposalRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FastSalesProposal.objects.select_related(
        'partner', 'partner_contact', 'salesperson',
    ).prefetch_related(
        'quotations__lines__product_variation',
        'quotations__lines__unit_of_measure',
        'quotations__currency',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FastSalesProposalReadSerializer
        return FastSalesProposalSerializer
    serializer_class = FastQuotationLineSerializer

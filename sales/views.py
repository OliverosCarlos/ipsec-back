from io import BytesIO
import os

from django.conf import settings as django_settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from xhtml2pdf import pisa

from .models import Quotation, QuotationLine, FastSalesProposal, FastQuotation, FastQuotationLine
from .serializers import (
    QuotationLineSerializer,
    QuotationReadSerializer,
    QuotationSerializer,
    ConvertToProposalSerializer,
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
    search_fields = ['name', 'description', 'proposal__name']
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


# ── Convertir FastQuotation a FastSalesProposal ─────────────

class FastQuotationConvertToProposalView(APIView):
    """POST /fast-quotations/<uuid:pk>/convert-to-proposal/"""

    def post(self, request, pk):
        try:
            quotation = FastQuotation.objects.get(pk=pk)
        except FastQuotation.DoesNotExist:
            return Response(
                {'detail': 'Cotización no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConvertToProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        proposal = quotation.convert_to_proposal(**serializer.validated_data)
        return Response(
            FastSalesProposalReadSerializer(proposal).data,
            status=status.HTTP_201_CREATED,
        )


# ── FastQuotation PDF Report ───────────────────────────────────

class FastQuotationPDFView(APIView):
    """GET /fast-quotations/<uuid:pk>/pdf/"""

    @staticmethod
    def _link_callback(uri, rel):
        """Resolve static/media URIs to absolute filesystem paths for xhtml2pdf."""
        if uri.startswith(django_settings.MEDIA_URL):
            path = os.path.join(
                django_settings.MEDIA_ROOT,
                uri.replace(django_settings.MEDIA_URL, ''),
            )
        elif uri.startswith(django_settings.STATIC_URL):
            path = os.path.join(
                django_settings.BASE_DIR,
                uri.replace(django_settings.STATIC_URL, 'sales/static/'),
            )
        else:
            return uri
        if os.path.isfile(path):
            return path
        return uri

    def get(self, request, pk):
        try:
            quotation = FastQuotation.objects.select_related(
                'proposal', 'currency', 'salesperson',
            ).get(pk=pk)
        except FastQuotation.DoesNotExist:
            return Response(
                {'detail': 'Cotización no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        lines = quotation.lines.select_related(
            'product_variation__product', 'unit_of_measure',
        ).order_by('sequence')

        html_string = render_to_string('sales/fast_quotation_pdf.html', {
            'quotation': quotation,
            'lines': lines,
            'now': timezone.now(),
        })

        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=buffer,
            encoding='utf-8',
            link_callback=self._link_callback,
        )

        if pisa_status.err:
            return Response(
                {'detail': 'Error al generar el PDF.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="FQ-{quotation.pk}.pdf"'
        return response

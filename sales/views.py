from io import BytesIO
import os
import zipfile

from django.conf import settings as django_settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from xhtml2pdf import pisa

from administration.models import Company
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
    ).prefetch_related('lines__product_service_variation', 'lines__clave_unidad')
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
    ).prefetch_related('lines__product_service_variation', 'lines__clave_unidad')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return QuotationReadSerializer
        return QuotationSerializer


# ── QuotationLine (standalone CRUD) ───────────────────────────

class QuotationLineListCreateView(generics.ListCreateAPIView):
    queryset = QuotationLine.objects.select_related(
        'quotation', 'product_service_variation', 'clave_unidad',
    )
    serializer_class = QuotationLineSerializer
    filterset_fields = ['quotation', 'product_service_variation', 'is_active']


class QuotationLineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = QuotationLine.objects.select_related(
        'quotation', 'product_service_variation', 'clave_unidad',
    )
    serializer_class = QuotationLineSerializer


# ── FastQuotation ──────────────────────────────────────────────

class FastQuotationListCreateView(generics.ListCreateAPIView):
    queryset = FastQuotation.objects.select_related(
        'proposal', 'currency', 'salesperson',
    ).prefetch_related('lines__product_service_variation', 'lines__clave_unidad')
    search_fields = ['name', 'description', 'proposal__name']
    filterset_fields = ['status', 'proposal', 'currency', 'salesperson', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FastQuotationReadSerializer
        return FastQuotationSerializer


class FastQuotationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FastQuotation.objects.select_related(
        'proposal', 'currency', 'salesperson',
    ).prefetch_related('lines__product_service_variation', 'lines__clave_unidad')
    search_fields = ['name', 'description', 'proposal__name']
    filterset_fields = ['status', 'proposal', 'currency', 'salesperson', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FastQuotationReadSerializer
        return FastQuotationSerializer


# ── FastQuotationLine (standalone CRUD) ────────────────────────

class FastQuotationLineListCreateView(generics.ListCreateAPIView):
    queryset = FastQuotationLine.objects.select_related(
        'fast_quotation', 'product_service_variation', 'clave_unidad',
    )
    serializer_class = FastQuotationLineSerializer
    filterset_fields = ['fast_quotation', 'product_service_variation', 'is_active']


class FastQuotationLineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FastQuotationLine.objects.select_related(
        'fast_quotation', 'product_service_variation', 'clave_unidad',
    )
    serializer_class = FastQuotationLineSerializer


# ── FastSalesProposal ────────────────────────────────────────

class FastSalesProposalListCreateView(generics.ListCreateAPIView):
    queryset = FastSalesProposal.objects.select_related(
        'partner', 'partner_contact', 'salesperson',
    ).prefetch_related(
        'quotations__lines__product_service_variation',
        'quotations__lines__clave_unidad',
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
        'quotations__lines__product_service_variation',
        'quotations__lines__clave_unidad',
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
            'product_service_variation__product', 'clave_unidad',
        ).order_by('sequence')

        company = Company.objects.prefetch_related(
            'addresses', 'bank_accounts__bank',
        ).first()

        html_string = render_to_string('sales/fast_quotation_pdf.html', {
            'quotation': quotation,
            'lines': lines,
            'company': company,
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


# ── FastSalesProposal – ZIP con todos los PDFs ────────────────

class FastSalesProposalPDFsView(APIView):
    """GET /fast-sales-proposals/<uuid:pk>/pdfs/

    Devuelve un archivo ZIP que contiene el PDF de cada cotización
    (FastQuotation) que pertenece a la propuesta de venta indicada.
    """

    @staticmethod
    def _link_callback(uri, rel):
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
            proposal = FastSalesProposal.objects.prefetch_related(
                'quotations__lines__product_service_variation__product',
                'quotations__lines__clave_unidad',
                'quotations__currency',
                'quotations__salesperson',
            ).get(pk=pk)
        except FastSalesProposal.DoesNotExist:
            return Response(
                {'detail': 'Propuesta no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        quotations = proposal.quotations.all()
        if not quotations.exists():
            return Response(
                {'detail': 'La propuesta no tiene cotizaciones.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        company = Company.objects.prefetch_related(
            'addresses', 'bank_accounts__bank',
        ).first()

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for quotation in quotations:
                lines = quotation.lines.select_related(
                    'product_service_variation__product', 'clave_unidad',
                ).order_by('sequence')

                html_string = render_to_string('sales/fast_quotation_pdf.html', {
                    'quotation': quotation,
                    'lines': lines,
                    'company': company,
                    'now': timezone.now(),
                })

                pdf_buffer = BytesIO()
                pisa_status = pisa.CreatePDF(
                    html_string,
                    dest=pdf_buffer,
                    encoding='utf-8',
                    link_callback=self._link_callback,
                )

                if pisa_status.err:
                    return Response(
                        {'detail': f'Error al generar el PDF de la cotización {quotation.pk}.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                filename = f'FQ-{quotation.pk}.pdf'
                zf.writestr(filename, pdf_buffer.getvalue())

        zip_buffer.seek(0)
        proposal_name = proposal.name.replace(' ', '_')
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = (
            f'attachment; filename="Propuesta-{proposal_name}.zip"'
        )
        return response

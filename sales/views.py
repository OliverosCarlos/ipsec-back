from io import BytesIO
import os
import zipfile
from datetime import timedelta
from decimal import Decimal

from django.conf import settings as django_settings
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
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


# ── Sales Dashboard ───────────────────────────────────────────

class SalesDashboardView(APIView):
    """
    GET /sales/dashboard/

    Devuelve métricas agregadas de Quotation, FastSalesProposal y FastQuotation
    para alimentar un dashboard de ventas.
    """

    def _counts_by_status(self, qs, choices):
        """Devuelve un dict {status_value: count} con todos los choices presentes."""
        raw = dict(qs.values_list('status').annotate(c=Count('id')))
        return {value: raw.get(value, 0) for value, _ in choices}

    def _monthly_amounts(self, qs, months=12):
        """Devuelve lista de {month: 'YYYY-MM', count, amount_total} de los últimos N meses."""
        today = timezone.now().date()
        start = (today.replace(day=1) - timedelta(days=31 * (months - 1))).replace(day=1)
        rows = (
            qs.filter(date__gte=start)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(count=Count('id'), amount_total=Sum('amount_total'))
            .order_by('month')
        )
        return [
            {
                'month': row['month'].strftime('%Y-%m'),
                'count': row['count'],
                'amount_total': str(row['amount_total'] or Decimal('0.00')),
            }
            for row in rows
        ]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        last_30 = today - timedelta(days=30)

        # ── Quotations ──
        quotations = Quotation.objects.all()
        quotations_active = quotations.filter(is_active=True)
        quotation_status = self._counts_by_status(quotations_active, Quotation.Status.choices)
        quotation_totals = quotations_active.aggregate(
            total_amount=Sum('amount_total'),
            total_subtotal=Sum('amount_subtotal'),
            total_tax=Sum('amount_tax'),
            total_discount=Sum('amount_discount'),
        )
        quotation_recent = quotations_active.filter(date__gte=last_30).aggregate(
            count=Count('id'),
            amount_total=Sum('amount_total'),
        )
        quotation_confirmed_amount = quotations_active.filter(
            status=Quotation.Status.CONFIRMED,
        ).aggregate(amount=Sum('amount_total'))['amount'] or Decimal('0.00')

        # ── FastSalesProposals ──
        proposals = FastSalesProposal.objects.all()
        proposals_active = proposals.filter(is_active=True)
        proposal_status = self._counts_by_status(proposals_active, FastSalesProposal.Status.choices)
        proposal_totals = proposals_active.aggregate(
            quotations_count=Count('quotations'),
            total_amount=Sum('quotations__amount_total'),
        )

        # ── FastQuotations ──
        fast_quotations = FastQuotation.objects.all()
        fast_quotations_active = fast_quotations.filter(is_active=True)
        fast_quotation_status = self._counts_by_status(
            fast_quotations_active, FastQuotation.Status.choices,
        )
        fast_quotation_totals = fast_quotations_active.aggregate(
            total_amount=Sum('amount_total'),
            total_subtotal=Sum('amount_subtotal'),
            total_tax=Sum('amount_tax'),
            total_discount=Sum('amount_discount'),
        )
        fast_quotation_recent = fast_quotations_active.filter(date__gte=last_30).aggregate(
            count=Count('id'),
            amount_total=Sum('amount_total'),
        )
        fast_quotation_confirmed_amount = fast_quotations_active.filter(
            status=FastQuotation.Status.CONFIRMED,
        ).aggregate(amount=Sum('amount_total'))['amount'] or Decimal('0.00')

        # ── FastQuotations sin propuesta ──
        fast_quotations_without_proposal = fast_quotations_active.filter(proposal__isnull=True).count()

        def _money(value):
            return str(value or Decimal('0.00'))

        data = {
            'generated_at': timezone.now().isoformat(),
            'quotations': {
                'total': quotations_active.count(),
                'by_status': quotation_status,
                'totals': {
                    'amount_total': _money(quotation_totals['total_amount']),
                    'amount_subtotal': _money(quotation_totals['total_subtotal']),
                    'amount_tax': _money(quotation_totals['total_tax']),
                    'amount_discount': _money(quotation_totals['total_discount']),
                    'confirmed_amount': _money(quotation_confirmed_amount),
                },
                'last_30_days': {
                    'count': quotation_recent['count'],
                    'amount_total': _money(quotation_recent['amount_total']),
                },
                'monthly': self._monthly_amounts(quotations_active),
            },
            'fast_sales_proposals': {
                'total': proposals_active.count(),
                'by_status': proposal_status,
                'totals': {
                    'quotations_count': proposal_totals['quotations_count'] or 0,
                    'amount_total': _money(proposal_totals['total_amount']),
                },
            },
            'fast_quotations': {
                'total': fast_quotations_active.count(),
                'without_proposal': fast_quotations_without_proposal,
                'by_status': fast_quotation_status,
                'totals': {
                    'amount_total': _money(fast_quotation_totals['total_amount']),
                    'amount_subtotal': _money(fast_quotation_totals['total_subtotal']),
                    'amount_tax': _money(fast_quotation_totals['total_tax']),
                    'amount_discount': _money(fast_quotation_totals['total_discount']),
                    'confirmed_amount': _money(fast_quotation_confirmed_amount),
                },
                'last_30_days': {
                    'count': fast_quotation_recent['count'],
                    'amount_total': _money(fast_quotation_recent['amount_total']),
                },
                'monthly': self._monthly_amounts(fast_quotations_active),
            },
        }
        return Response(data, status=status.HTTP_200_OK)

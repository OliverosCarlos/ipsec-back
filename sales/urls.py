from django.urls import path

from .views import (
    QuotationLineListCreateView,
    QuotationLineRetrieveUpdateDestroyView,
    QuotationListCreateView,
    QuotationRetrieveUpdateDestroyView,
    FastQuotationLineListCreateView,
    FastQuotationLineRetrieveUpdateDestroyView,
    FastQuotationListCreateView,
    FastQuotationRetrieveUpdateDestroyView,
    FastSalesProposalListCreateView,
    FastSalesProposalRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('quotations/', QuotationListCreateView.as_view(), name='quotation-list-create'),
    path('quotations/<uuid:pk>/', QuotationRetrieveUpdateDestroyView.as_view(), name='quotation-detail'),
    path('quotation-lines/', QuotationLineListCreateView.as_view(), name='quotation-line-list-create'),
    path('quotation-lines/<uuid:pk>/', QuotationLineRetrieveUpdateDestroyView.as_view(), name='quotation-line-detail'),
    path('fast-sales-proposals/', FastSalesProposalListCreateView.as_view(), name='fast-sales-proposal-list-create'),
    path('fast-sales-proposals/<uuid:pk>/', FastSalesProposalRetrieveUpdateDestroyView.as_view(), name='fast-sales-proposal-detail'),
    path('fast-quotations/', FastQuotationListCreateView.as_view(), name='fast-quotation-list-create'),
    path('fast-quotations/<uuid:pk>/', FastQuotationRetrieveUpdateDestroyView.as_view(), name='fast-quotation-detail'),
    path('fast-quotation-lines/', FastQuotationLineListCreateView.as_view(), name='fast-quotation-line-list-create'),
    path('fast-quotation-lines/<uuid:pk>/', FastQuotationLineRetrieveUpdateDestroyView.as_view(), name='fast-quotation-line-detail'),
]

import django_filters

from .models import FastQuotation, FastSalesProposal, Quotation, SalesProposal


class QuotationFilter(django_filters.FilterSet):
    number = django_filters.CharFilter(lookup_expr='icontains')
    partner_legal_name = django_filters.CharFilter(field_name='partner__legal_name', lookup_expr='icontains')
    partner_contact_name = django_filters.CharFilter(field_name='partner_contact__name', lookup_expr='icontains')
    date = django_filters.DateFilter(field_name='date', lookup_expr='exact')
    validity_date = django_filters.DateFilter(field_name='validity_date', lookup_expr='exact')
    amount_total = django_filters.NumberFilter(field_name='amount_total', lookup_expr='exact')

    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    partner = django_filters.UUIDFilter(field_name='partner')
    currency = django_filters.UUIDFilter(field_name='currency')
    salesperson = django_filters.UUIDFilter(field_name='salesperson')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Quotation
        fields = [
            'number',
            'partner_legal_name',
            'partner_contact_name',
            'date',
            'validity_date',
            'amount_total',
            'status',
            'partner',
            'currency',
            'salesperson',
            'is_active',
        ]


class SalesProposalFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    objective = django_filters.CharFilter(lookup_expr='icontains')
    partner_legal_name = django_filters.CharFilter(field_name='partner__legal_name', lookup_expr='icontains')
    partner_contact_name = django_filters.CharFilter(field_name='partner_contact__name', lookup_expr='icontains')
    status = django_filters.MultipleChoiceFilter(choices=SalesProposal.Status.choices)
    partner = django_filters.UUIDFilter(field_name='partner')
    salesperson = django_filters.UUIDFilter(field_name='salesperson')
    created_at_after = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_at_before = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = SalesProposal
        fields = [
            'name',
            'objective',
            'partner_legal_name',
            'partner_contact_name',
            'status',
            'partner',
            'salesperson',
            'created_at_after',
            'created_at_before',
            'is_active',
        ]


class FastSalesProposalFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    objective = django_filters.CharFilter(lookup_expr='icontains')
    partner_legal_name = django_filters.CharFilter(field_name='partner__legal_name', lookup_expr='icontains')
    partner_contact_name = django_filters.CharFilter(field_name='partner_contact__name', lookup_expr='icontains')
    status = django_filters.MultipleChoiceFilter(choices=FastSalesProposal.Status.choices)
    partner = django_filters.UUIDFilter(field_name='partner')
    salesperson = django_filters.UUIDFilter(field_name='salesperson')
    created_at_after = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_at_before = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = FastSalesProposal
        fields = [
            'name',
            'objective',
            'partner_legal_name',
            'partner_contact_name',
            'status',
            'partner',
            'salesperson',
            'created_at_after',
            'created_at_before',
            'is_active',
        ]


class FastQuotationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    proposal_name = django_filters.CharFilter(field_name='proposal__name', lookup_expr='icontains')
    date = django_filters.DateFilter(field_name='date', lookup_expr='exact')
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    validity_date = django_filters.DateFilter(field_name='validity_date', lookup_expr='exact')
    amount_total = django_filters.NumberFilter(field_name='amount_total', lookup_expr='exact')
    amount_total_min = django_filters.NumberFilter(field_name='amount_total', lookup_expr='gte')
    amount_total_max = django_filters.NumberFilter(field_name='amount_total', lookup_expr='lte')
    status = django_filters.MultipleChoiceFilter(choices=FastQuotation.Status.choices)
    proposal = django_filters.UUIDFilter(field_name='proposal')
    currency = django_filters.UUIDFilter(field_name='currency')
    salesperson = django_filters.UUIDFilter(field_name='salesperson')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = FastQuotation
        fields = [
            'name',
            'description',
            'proposal_name',
            'date',
            'date_after',
            'date_before',
            'validity_date',
            'amount_total',
            'amount_total_min',
            'amount_total_max',
            'status',
            'proposal',
            'currency',
            'salesperson',
            'is_active',
        ]

import django_filters

from .models import Partner


class PartnerFilter(django_filters.FilterSet):
    sector = django_filters.CharFilter(lookup_expr='iexact')
    person_type = django_filters.CharFilter(lookup_expr='iexact')
    company_sector = django_filters.CharFilter(field_name='company_sector__name', lookup_expr='icontains')
    commercial_name = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.CharFilter(
        field_name='roles__role',
        lookup_expr='iexact',
        label='Rol del partner (CUSTOMER, SUPPLIER, CARRIER, OTHER)',
    )

    class Meta:
        model = Partner
        fields = ['sector', 'person_type', 'company_sector', 'commercial_name', 'role']

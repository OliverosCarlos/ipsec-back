import django_filters

from .models import Brand


class BrandFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Brand
        fields = ['code', 'name']

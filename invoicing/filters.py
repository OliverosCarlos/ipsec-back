import django_filters

from .models import ClaveProdServ, ClaveUnidad, SatCatalog


class SatCatalogFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='icontains')
    catalog = django_filters.CharFilter(lookup_expr='iexact')
    description = django_filters.CharFilter(lookup_expr='icontains')
    valid_from = django_filters.DateFilter(field_name='valid_from', lookup_expr='gte')
    valid_to = django_filters.DateFilter(field_name='valid_to', lookup_expr='lte')

    class Meta:
        model = SatCatalog
        fields = ['code', 'catalog', 'description', 'valid_from', 'valid_to']


class ClaveProdServFilter(django_filters.FilterSet):
    clave = django_filters.CharFilter(lookup_expr='istartswith')
    descripcion = django_filters.CharFilter(lookup_expr='icontains')
    palabras_similares = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ClaveProdServ
        fields = ['clave', 'descripcion', 'palabras_similares']


class ClaveUnidadFilter(django_filters.FilterSet):
    clave = django_filters.CharFilter(lookup_expr='istartswith')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ClaveUnidad
        fields = ['clave', 'name']

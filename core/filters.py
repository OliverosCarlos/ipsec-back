import django_filters

from .models import EntityModel


class EntityModelFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    plural_name = django_filters.CharFilter(lookup_expr='icontains')
    model = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = EntityModel
        fields = ['code', 'name', 'plural_name', 'model', 'is_active']
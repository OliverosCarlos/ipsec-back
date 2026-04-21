import django_filters

from .models import Brand, ProdServ, ProdServVariation


class BrandFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Brand
        fields = ['code', 'name']


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    short_description = django_filters.CharFilter(lookup_expr='icontains')
    long_description = django_filters.CharFilter(lookup_expr='icontains')
    product_type = django_filters.CharFilter(
        field_name='product_type__name', lookup_expr='icontains'
    )
    brand = django_filters.NumberFilter()
    category = django_filters.NumberFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = ProdServ
        fields = ['name', 'short_description', 'long_description', 'product_type', 'brand', 'category', 'is_active']


class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    short_description = django_filters.CharFilter(lookup_expr='icontains')
    long_description = django_filters.CharFilter(lookup_expr='icontains')
    product_type = django_filters.CharFilter(
        field_name='product_type__name', lookup_expr='icontains'
    )

    class Meta:
        model = ProdServ
        fields = ['name', 'short_description', 'long_description', 'product_type']


class ResourceItemFilter(django_filters.FilterSet):
    # Variation fields
    reference = django_filters.CharFilter(lookup_expr='icontains')
    override_name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    product = django_filters.UUIDFilter(field_name='product__id')

    # Product (parent) fields
    name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    short_description = django_filters.CharFilter(
        field_name='product__short_description', lookup_expr='icontains'
    )
    long_description = django_filters.CharFilter(
        field_name='product__long_description', lookup_expr='icontains'
    )
    brand = django_filters.NumberFilter(field_name='product__brand_id')
    brand_name = django_filters.CharFilter(field_name='product__brand__name', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='product__category_id')
    category_name = django_filters.CharFilter(
        field_name='product__category__name', lookup_expr='icontains'
    )
    product_type = django_filters.NumberFilter(field_name='product__product_type_id')
    product_type_name = django_filters.CharFilter(
        field_name='product__product_type__name', lookup_expr='icontains'
    )
    partner = django_filters.NumberFilter(field_name='product__partners__id')

    class Meta:
        model = ProdServVariation
        fields = [
            'reference', 'override_name', 'is_active', 'product',
            'name', 'short_description', 'long_description',
            'brand', 'brand_name', 'category', 'category_name',
            'product_type', 'product_type_name', 'partner',
        ]

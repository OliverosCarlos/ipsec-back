from rest_framework import generics

from .models import (
    Brand,
    Product,
    Category,
    ProductVariation,
    Type,
    UnitOfMeasure,
)
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductVariationSerializer,
    ProductSerializer,
    TypeSerializer,
    UnitOfMeasureSerializer,
)


# ── Brand ──────────────────────────────────────────────────────────────────────

class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    search_fields = ['name']


class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


# ── Type ──────────────────────────────────────────────────────────────

class TypeListCreateView(generics.ListCreateAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    search_fields = ['name', 'code']


class TypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


# ── Category ──────────────────────────────────────────────────────────

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'code']


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ── Unit of Measure ────────────────────────────────────────────────────────────

class UnitOfMeasureListCreateView(generics.ListCreateAPIView):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    search_fields = ['name', 'abbreviation']


class UnitOfMeasureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer


# ── Product ────────────────────────────────────────────────────────────────────

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related(
        'brand',
        'category',
        'product_type',
        'inventory_account',
    ).prefetch_related(
        'suppliers',
        'variations__unit_of_measure',
    )
    serializer_class = ProductSerializer
    search_fields = ['short_name', 'long_name', 'sku']
    filterset_fields = ['brand', 'category', 'product_type', 'is_active']


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related(
        'brand',
        'category',
        'product_type',
        'inventory_account',
    ).prefetch_related(
        'suppliers',
        'variations__unit_of_measure',
    )
    serializer_class = ProductSerializer


# ── Product Variation ─────────────────────────────────────────────────────────

class ProductVariationListCreateView(generics.ListCreateAPIView):
    queryset = ProductVariation.objects.select_related(
        'product', 'unit_of_measure',
    )
    serializer_class = ProductVariationSerializer
    search_fields = ['barcode']
    filterset_fields = ['product', 'unit_of_measure', 'is_active']


class ProductVariationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductVariation.objects.select_related(
        'product', 'unit_of_measure',
    )
    serializer_class = ProductVariationSerializer

from django.urls import path

from .views import (
    BrandListCreateView,
    BrandRetrieveUpdateDestroyView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    ProductVariationListCreateView,
    ProductVariationRetrieveUpdateDestroyView,
    TypeListCreateView,
    TypeRetrieveUpdateDestroyView,
    UnitOfMeasureListCreateView,
    UnitOfMeasureRetrieveUpdateDestroyView,
)

urlpatterns = [
    # Brands
    path('brands/', BrandListCreateView.as_view(), name='brand-list-create'),
    path('brands/<int:pk>/', BrandRetrieveUpdateDestroyView.as_view(), name='brand-detail'),

    # Types
    path('types/', TypeListCreateView.as_view(), name='type-list-create'),
    path('types/<int:pk>/', TypeRetrieveUpdateDestroyView.as_view(), name='type-detail'),

    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),

    # Units of Measure
    path('units-of-measure/', UnitOfMeasureListCreateView.as_view(), name='unit-of-measure-list-create'),
    path('units-of-measure/<int:pk>/', UnitOfMeasureRetrieveUpdateDestroyView.as_view(), name='unit-of-measure-detail'),

    # Products
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),

    # Product Variations
    path('product-variations/', ProductVariationListCreateView.as_view(), name='product-variation-list-create'),
    path('product-variations/<int:pk>/', ProductVariationRetrieveUpdateDestroyView.as_view(), name='product-variation-detail'),
]

from django.urls import path

from .views import (
    BrandListCreateView,
    BrandRetrieveUpdateDestroyView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    PriceListListCreateView,
    PriceListRetrieveUpdateDestroyView,
    PriceListItemListCreateView,
    PriceListItemRetrieveUpdateDestroyView,
    ProductBulkUpdateView,
    ProductListCreateView,
    ResourceItemListView,
    ProductRetrieveUpdateDestroyView,
    ProductVariationListCreateView,
    ProductVariationRetrieveUpdateDestroyView,
    ServiceListCreateView,
    ServiceRetrieveUpdateDestroyView,
    ServiceVariationListCreateView,
    ServiceVariationRetrieveUpdateDestroyView,
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
    path('products/<uuid:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('products/<uuid:pk>/bulk-update/', ProductBulkUpdateView.as_view(), name='product-bulk-update'),

    # Product Variations
    path('product-variations/', ProductVariationListCreateView.as_view(), name='product-variation-list-create'),
    path('product-variations/<uuid:pk>/', ProductVariationRetrieveUpdateDestroyView.as_view(), name='product-variation-detail'),
    path('resource-items/', ResourceItemListView.as_view(), name='resource-item-list'),

    # Services
    path('services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<uuid:pk>/', ServiceRetrieveUpdateDestroyView.as_view(), name='service-detail'),

    # Service Variations
    path('service-variations/', ServiceVariationListCreateView.as_view(), name='service-variation-list-create'),
    path('service-variations/<uuid:pk>/', ServiceVariationRetrieveUpdateDestroyView.as_view(), name='service-variation-detail'),

    # Price Lists
    path('price-lists/', PriceListListCreateView.as_view(), name='price-list-list-create'),
    path('price-lists/<uuid:pk>/', PriceListRetrieveUpdateDestroyView.as_view(), name='price-list-detail'),

    # Price List Items
    path('price-list-items/', PriceListItemListCreateView.as_view(), name='price-list-item-list-create'),
    path('price-list-items/<uuid:pk>/', PriceListItemRetrieveUpdateDestroyView.as_view(), name='price-list-item-detail'),

    
]

from django.urls import path

from .views import (
    ClaveProdServListView,
    ClaveProdServSearchView,
    ClaveUnidadListView,
    ClaveUnidadSearchView,
    PriceListItemListCreateView,
    PriceListItemRetrieveUpdateDestroyView,
    PriceListListCreateView,
    PriceListRetrieveUpdateDestroyView,
    SatCatalogBulkCreateView,
    SatCatalogListCreateView,
    SatCatalogRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('price-lists/', PriceListListCreateView.as_view(), name='price-list-list-create'),
    path('price-lists/<int:pk>/', PriceListRetrieveUpdateDestroyView.as_view(), name='price-list-detail'),

    path('price-list-items/', PriceListItemListCreateView.as_view(), name='price-list-item-list-create'),
    path('price-list-items/<int:pk>/', PriceListItemRetrieveUpdateDestroyView.as_view(), name='price-list-item-detail'),

    path('sat-catalogs/', SatCatalogListCreateView.as_view(), name='sat-catalog-list-create'),
    path('sat-catalogs/bulk/', SatCatalogBulkCreateView.as_view(), name='sat-catalog-bulk-create'),
    path('sat-catalogs/<str:code>/', SatCatalogRetrieveUpdateDestroyView.as_view(), name='sat-catalog-detail'),

    path('claves-prod-serv/', ClaveProdServListView.as_view(), name='clave-prod-serv-list'),
    path('claves-prod-serv/search/', ClaveProdServSearchView.as_view(), name='clave-prod-serv-search'),

    path('claves-unit/', ClaveUnidadListView.as_view(), name='clave-unidad-list'),
    path('claves-unit/search/', ClaveUnidadSearchView.as_view(), name='clave-unidad-search'),
]

from django.urls import path

from .views import (
    PriceListItemListCreateView,
    PriceListItemRetrieveUpdateDestroyView,
    PriceListListCreateView,
    PriceListRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('price-lists/', PriceListListCreateView.as_view(), name='price-list-list-create'),
    path('price-lists/<int:pk>/', PriceListRetrieveUpdateDestroyView.as_view(), name='price-list-detail'),

    path('price-list-items/', PriceListItemListCreateView.as_view(), name='price-list-item-list-create'),
    path('price-list-items/<int:pk>/', PriceListItemRetrieveUpdateDestroyView.as_view(), name='price-list-item-detail'),
]

from django.urls import path

from .views import (
    StockAdjustmentListCreateView,
    StockAdjustmentRetrieveUpdateDestroyView,
    StockItemListCreateView,
    StockItemRetrieveUpdateDestroyView,
    StockMovementListCreateView,
    StockMovementRetrieveUpdateDestroyView,
    WarehouseListCreateView,
    WarehouseRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('warehouses/', WarehouseListCreateView.as_view(), name='warehouse-list-create'),
    path('warehouses/<int:pk>/', WarehouseRetrieveUpdateDestroyView.as_view(), name='warehouse-detail'),

    path('stock-items/', StockItemListCreateView.as_view(), name='stock-item-list-create'),
    path('stock-items/<int:pk>/', StockItemRetrieveUpdateDestroyView.as_view(), name='stock-item-detail'),

    path('stock-movements/', StockMovementListCreateView.as_view(), name='stock-movement-list-create'),
    path('stock-movements/<int:pk>/', StockMovementRetrieveUpdateDestroyView.as_view(), name='stock-movement-detail'),

    path('stock-adjustments/', StockAdjustmentListCreateView.as_view(), name='stock-adjustment-list-create'),
    path('stock-adjustments/<int:pk>/', StockAdjustmentRetrieveUpdateDestroyView.as_view(), name='stock-adjustment-detail'),
]

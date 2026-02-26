from django.urls import path

from .views import SupplierListCreateView, SupplierRetrieveUpdateDestroyView

urlpatterns = [
    path('suppliers/', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierRetrieveUpdateDestroyView.as_view(), name='supplier-detail'),
]

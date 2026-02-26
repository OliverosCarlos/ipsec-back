from rest_framework import generics

from .models import Supplier
from .serializers import SupplierSerializer


class SupplierListCreateView(generics.ListCreateAPIView):
	queryset = Supplier.objects.all()
	serializer_class = SupplierSerializer
	search_fields = ['name', 'code', 'tax_id']
	filterset_fields = ['is_active']


class SupplierRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Supplier.objects.all()
	serializer_class = SupplierSerializer

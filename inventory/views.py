from rest_framework import generics

from .models import StockAdjustment, StockItem, StockMovement, Warehouse
from .serializers import (
	StockAdjustmentSerializer,
	StockItemSerializer,
	StockMovementSerializer,
	WarehouseSerializer,
)


class WarehouseListCreateView(generics.ListCreateAPIView):
	queryset = Warehouse.objects.all()
	serializer_class = WarehouseSerializer
	search_fields = ['name', 'code']
	filterset_fields = ['is_active']


class WarehouseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Warehouse.objects.all()
	serializer_class = WarehouseSerializer


class StockItemListCreateView(generics.ListCreateAPIView):
	queryset = StockItem.objects.select_related('product_variation', 'warehouse')
	serializer_class = StockItemSerializer
	filterset_fields = ['warehouse', 'product_variation']


class StockItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = StockItem.objects.select_related('product_variation', 'warehouse')
	serializer_class = StockItemSerializer


class StockMovementListCreateView(generics.ListCreateAPIView):
	queryset = StockMovement.objects.select_related('product_variation', 'warehouse')
	serializer_class = StockMovementSerializer
	filterset_fields = ['warehouse', 'product_variation', 'movement_type']


class StockMovementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = StockMovement.objects.select_related('product_variation', 'warehouse')
	serializer_class = StockMovementSerializer


class StockAdjustmentListCreateView(generics.ListCreateAPIView):
	queryset = StockAdjustment.objects.select_related('product_variation', 'warehouse')
	serializer_class = StockAdjustmentSerializer
	filterset_fields = ['warehouse', 'product_variation']


class StockAdjustmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = StockAdjustment.objects.select_related('product_variation', 'warehouse')
	serializer_class = StockAdjustmentSerializer

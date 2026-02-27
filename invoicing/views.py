from rest_framework import generics

from .models import PriceList, PriceListItem
from .serializers import PriceListItemSerializer, PriceListSerializer


class PriceListListCreateView(generics.ListCreateAPIView):
	queryset = PriceList.objects.all()
	serializer_class = PriceListSerializer
	search_fields = ['name', 'code']
	filterset_fields = ['is_active', 'currency']


class PriceListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PriceList.objects.all()
	serializer_class = PriceListSerializer


class PriceListItemListCreateView(generics.ListCreateAPIView):
	queryset = PriceListItem.objects.select_related('price_list', 'product_variation')
	serializer_class = PriceListItemSerializer
	filterset_fields = ['price_list', 'product_variation']


class PriceListItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = PriceListItem.objects.select_related('price_list', 'product_variation')
	serializer_class = PriceListItemSerializer

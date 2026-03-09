from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .pagination import SatCatalogPagination

from .filters import SatCatalogFilter
from .models import PriceList, PriceListItem, SatCatalog
from .serializers import PriceListItemSerializer, PriceListSerializer, SatCatalogSerializer



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


class SatCatalogListCreateView(generics.ListCreateAPIView):
	queryset = SatCatalog.objects.all()
	serializer_class = SatCatalogSerializer
	filterset_class = SatCatalogFilter
	search_fields = ['code', 'catalog', 'description']
	pagination_class = SatCatalogPagination


class SatCatalogRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
	queryset = SatCatalog.objects.all()
	serializer_class = SatCatalogSerializer
	lookup_field = 'code'


class SatCatalogBulkCreateView(APIView):
	def post(self, request, *args, **kwargs):
		serializer = SatCatalogSerializer(data=request.data, many=True)
		serializer.is_valid(raise_exception=True)

		with transaction.atomic():
			serializer.save()

		return Response(serializer.data, status=status.HTTP_201_CREATED)

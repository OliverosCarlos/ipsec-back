from django.contrib.postgres.search import TrigramSimilarity
from django.db import transaction
from django.db.models import Value
from django.db.models.functions import Coalesce, Greatest
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .pagination import SatCatalogPagination

from .filters import ClaveProdServFilter, ClaveUnidadFilter, SatCatalogFilter
from .models import ClaveProdServ, ClaveUnidad, PriceList, PriceListItem, SatCatalog
from .serializers import (
	ClaveProdServSerializer, ClaveProdServSearchSerializer,
	ClaveUnidadSerializer, ClaveUnidadSearchSerializer,
	PriceListItemSerializer, PriceListSerializer, SatCatalogSerializer,
)



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


class ClaveProdServListView(generics.ListAPIView):
	queryset = ClaveProdServ.objects.all()
	serializer_class = ClaveProdServSerializer
	filterset_class = ClaveProdServFilter
	search_fields = ['clave', 'descripcion', 'palabras_similares']
	pagination_class = SatCatalogPagination


class ClaveProdServSearchView(generics.ListAPIView):
	"""
	Búsqueda inteligente de ClaveProdServ usando TrigramSimilarity.

	Query params:
	  - q (requerido): texto a buscar (clave, descripción o palabras similares).
	  - threshold (opcional, default 0.1): similitud mínima (0.0 – 1.0).

	Retorna resultados ordenados por mayor similitud, con el campo `similarity`.
	"""
	serializer_class = ClaveProdServSearchSerializer
	pagination_class = SatCatalogPagination

	def get_queryset(self):
		query = self.request.query_params.get('q', '').strip()
		threshold = self.request.query_params.get('threshold', '0.1')

		try:
			threshold = max(0.0, min(float(threshold), 1.0))
		except (ValueError, TypeError):
			threshold = 0.1

		if not query:
			return ClaveProdServ.objects.none()

		return (
			ClaveProdServ.objects
			.annotate(
				sim_clave=TrigramSimilarity('clave', query),
				sim_descripcion=TrigramSimilarity('descripcion', query),
				sim_palabras=TrigramSimilarity(
					Coalesce('palabras_similares', Value('')), query
				),
				similarity=Greatest(
					'sim_clave', 'sim_descripcion', 'sim_palabras'
				),
			)
			.filter(similarity__gte=threshold)
			.order_by('-similarity')
		)


class ClaveUnidadListView(generics.ListAPIView):
	queryset = ClaveUnidad.objects.all()
	serializer_class = ClaveUnidadSerializer
	filterset_class = ClaveUnidadFilter
	search_fields = ['clave', 'name']
	pagination_class = SatCatalogPagination


class ClaveUnidadSearchView(generics.ListAPIView):
	"""
	Búsqueda inteligente de ClaveUnidad usando TrigramSimilarity.

	Query params:
	  - q (requerido): texto a buscar (clave o nombre).
	  - threshold (opcional, default 0.1): similitud mínima (0.0 – 1.0).

	Retorna resultados ordenados por mayor similitud, con el campo `similarity`.
	"""
	serializer_class = ClaveUnidadSearchSerializer
	pagination_class = SatCatalogPagination

	def get_queryset(self):
		query = self.request.query_params.get('q', '').strip()
		threshold = self.request.query_params.get('threshold', '0.1')

		try:
			threshold = max(0.0, min(float(threshold), 1.0))
		except (ValueError, TypeError):
			threshold = 0.1

		if not query:
			return ClaveUnidad.objects.none()

		return (
			ClaveUnidad.objects
			.annotate(
				sim_clave=TrigramSimilarity('clave', query),
				sim_name=TrigramSimilarity('name', query),
				similarity=Greatest('sim_clave', 'sim_name'),
			)
			.filter(similarity__gte=threshold)
			.order_by('-similarity')
		)

from itertools import chain

from django.db import models
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import BrandFilter, ProductFilter, ResourceItemFilter, ServiceFilter
from .pagination import ResourcePagination

from .models import (
    Brand,
    ProdServ,
    Category,
    PriceList,
    PriceListItem,
    ProdServVariation,
    Type,
    UnitOfMeasure,
)
from .serializers import (
    BrandSerializer,
    ResourceItemSerializer,
    CategorySerializer,
    PriceListSerializer,
    PriceListItemSerializer,
    ProdServVariationSerializer,
    ProdServVariationReadSerializer,
    ProdServReadSerializer,
    ProdServWriteSerializer,
    ProductBulkUpdateSerializer,
    ServiceBulkUpdateSerializer,
    ServiceVariationSerializer,
    ServiceVariationReadSerializer,
    ServiceReadSerializer,
    ServiceWriteSerializer,
    TypeSerializer,
    UnitOfMeasureSerializer,
)


# ── Brand ──────────────────────────────────────────────────────────────────────

class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filterset_class = BrandFilter
    search_fields = ['name']


class BrandRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


# ── Type ──────────────────────────────────────────────────────────────

class TypeListCreateView(generics.ListCreateAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    search_fields = ['name', 'code']


class TypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


# ── Category ──────────────────────────────────────────────────────────

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'code']


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ── Unit of Measure ────────────────────────────────────────────────────────────

class UnitOfMeasureListCreateView(generics.ListCreateAPIView):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    search_fields = ['name', 'abbreviation']


class UnitOfMeasureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer


# ── Product ────────────────────────────────────────────────────────────────────

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = ProdServ.objects.select_related(
        'brand',
        'category',
        'product_type',
    ).prefetch_related(
        'partners',
        'variations',
        'variations__sat_detail',
        'variations__inventory_detail',
    )
    pagination_class = ResourcePagination
    search_fields = ['name']
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProdServReadSerializer
        return ProdServWriteSerializer

    def perform_create(self, serializer):
        inventory_type = Type.objects.filter(name__iexact='inventario').first()
        if not inventory_type:
            raise ValidationError({'product_type': 'No existe un tipo con nombre "inventario".'})
        serializer.save(product_type=inventory_type)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProdServ.objects.select_related(
        'brand',
        'category',
        'product_type',
    ).prefetch_related(
        'partners',
        'variations',
        'variations__sat_detail',
        'variations__inventory_detail',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProdServReadSerializer
        return ProdServWriteSerializer


# ── Product Bulk Update ────────────────────────────────────────────────────────

class ProductBulkUpdateView(APIView):
    """
    Actualización integral de un Product y sus variaciones.
    Cada variación envía un campo 'action': created, updated o deleted.

    PUT /products/<pk>/bulk-update/
    {
        "name": "Nuevo nombre",
        "clave_prod_serv": "01010101",
        "objeto_imp": "02",
        "variations": [
            {"action": "created", "base_price": "100.00", ...},
            {"action": "updated", "id": "<uuid>", "base_price": "120.00", ...},
            {"action": "deleted", "id": "<uuid>"}
        ]
    }
    """

    def put(self, request, pk):
        from django.db import transaction
        from inventory.models import ProductVariationInventory
        from invoicing.models.general import ProdServVariationSAT
        from invoicing.models.sat import ClaveUnidad, SatCatalog

        try:
            product = ProdServ.objects.get(pk=pk)
        except ProdServ.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        variations_data = data.pop('variations', None)
        partners_data = data.pop('partners', None)
        clave_prod_serv = data.pop('clave_prod_serv', '')
        objeto_imp = data.pop('objeto_imp', '')
        product_fields = data

        result = {'product_updated': False, 'partners_updated': False, 'variations': {}}

        def resolve_sat_catalog(catalog, pk):
            if not pk:
                return None
            return SatCatalog.objects.filter(catalog=catalog, pk=pk).first()

        def create_sat_detail(sat_fields):
            clave_unidad_code = sat_fields.pop('clave_unidad', '')
            return ProdServVariationSAT.objects.create(
                clave_prod_serv_id=clave_prod_serv or None,
                objeto_imp=resolve_sat_catalog('c_ObjetoImp', objeto_imp),
                clave_unidad_id=clave_unidad_code or None,
                **sat_fields,
            )

        def create_inventory_detail(inv_fields):
            if not inv_fields.get('sku'):
                return None
            return ProductVariationInventory.objects.create(**inv_fields)

        def extract_sat_fields(item):
            return {
                'clave_unidad': item.pop('clave_unidad', ''),
                'unidad': item.pop('unidad', ''),
            }

        def extract_inventory_fields(item):
            return {
                'sku': item.pop('sku', ''),
                'barcode': item.pop('barcode', ''),
                'description': item.pop('inventory_description', ''),
            }

        with transaction.atomic():
            # ── Update Product fields ──
            if product_fields:
                for attr, value in product_fields.items():
                    setattr(product, attr, value)
                product.save()
                result['product_updated'] = True

            # ── Update Partners (M2M) ──
            if partners_data is not None:
                product.partners.set(partners_data)
                result['partners_updated'] = True

            # ── Process variations ──
            if variations_data is not None:
                created = []
                updated = []
                deleted = []

                for item in variations_data:
                    action = item.pop('action')
                    item_id = item.pop('id', None)
                    sat_fields = extract_sat_fields(item)
                    inv_fields = extract_inventory_fields(item)

                    if action == 'created':
                        sat_detail = create_sat_detail(sat_fields)
                        inventory_detail = create_inventory_detail(inv_fields)
                        obj = ProdServVariation.objects.create(
                            product=product,
                            sat_detail=sat_detail,
                            inventory_detail=inventory_detail,
                            **item,
                        )
                        created.append(str(obj.id))

                    elif action == 'updated':
                        try:
                            variation = ProdServVariation.objects.get(id=item_id, product=product)
                        except ProdServVariation.DoesNotExist:
                            continue

                        # Update SAT detail
                        if variation.sat_detail:
                            clave_unidad_code = sat_fields.pop('clave_unidad', '')
                            update_kwargs = {'unidad': sat_fields.get('unidad', '')}
                            update_kwargs['clave_prod_serv_id'] = clave_prod_serv or variation.sat_detail.clave_prod_serv_id
                            objeto_imp_instance = resolve_sat_catalog('c_ObjetoImp', objeto_imp)
                            update_kwargs['objeto_imp'] = objeto_imp_instance if objeto_imp_instance else variation.sat_detail.objeto_imp
                            clave_unidad_instance = ClaveUnidad.objects.filter(clave=clave_unidad_code).first()
                            update_kwargs['clave_unidad'] = clave_unidad_instance if clave_unidad_instance else variation.sat_detail.clave_unidad
                            ProdServVariationSAT.objects.filter(id=variation.sat_detail_id).update(**update_kwargs)
                        else:
                            variation.sat_detail = create_sat_detail(sat_fields)

                        # Update inventory detail
                        if variation.inventory_detail and inv_fields.get('sku'):
                            ProductVariationInventory.objects.filter(id=variation.inventory_detail_id).update(**inv_fields)
                        elif not variation.inventory_detail and inv_fields.get('sku'):
                            variation.inventory_detail = create_inventory_detail(inv_fields)

                        # Update variation fields
                        for attr, value in item.items():
                            setattr(variation, attr, value)
                        variation.save()
                        updated.append(str(item_id))

                    elif action == 'deleted':
                        ProdServVariation.objects.filter(id=item_id, product=product).delete()
                        deleted.append(str(item_id))

                result['variations'] = {'created': created, 'updated': updated, 'deleted': deleted}

        return Response(result, status=status.HTTP_200_OK)


# ── Product Variation ─────────────────────────────────────────────────────────

class ProductVariationListCreateView(generics.ListCreateAPIView):
    queryset = ProdServVariation.objects.select_related(
        'product',
        'sat_detail',
        'sat_detail__clave_prod_serv',
        'sat_detail__clave_unidad',
        'sat_detail__objeto_imp',
        'inventory_detail',
        'service_detail',
    )
    search_fields = ['override_name']
    filterset_fields = ['product', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProdServVariationReadSerializer
        return ProdServVariationSerializer


class ProductVariationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProdServVariation.objects.select_related(
        'product',
        'sat_detail',
        'sat_detail__clave_prod_serv',
        'sat_detail__clave_unidad',
        'sat_detail__objeto_imp',
        'inventory_detail',
        'service_detail',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProdServVariationReadSerializer
        return ProdServVariationSerializer


class ResourceItemListView(generics.ListAPIView):
    queryset = ProdServVariation.objects.select_related(
        'product',
        'product__brand',
        'product__category',
        'product__product_type',
        'sat_detail',
        'sat_detail__clave_prod_serv',
        'sat_detail__clave_unidad',
        'sat_detail__objeto_imp',
        'inventory_detail',
        'service_detail',
    ).prefetch_related(
        'product__partners',
    )
    serializer_class = ResourceItemSerializer
    pagination_class = None
    filterset_class = ResourceItemFilter
    search_fields = [
        'override_name',
        'reference',
        'product__name',
        'product__short_description',
    ]


# ── Service ────────────────────────────────────────────────────────────────────

class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = ProdServ.objects.select_related(
        'brand',
        'category',
        'product_type',
    ).prefetch_related(
        'partners',
        'variations',
        'variations__sat_detail',
        'variations__service_detail',
    )
    pagination_class = ResourcePagination
    search_fields = ['name']
    filterset_class = ServiceFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceReadSerializer
        return ServiceWriteSerializer


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProdServ.objects.select_related(
        'brand',
        'category',
        'product_type',
    ).prefetch_related(
        'partners',
        'variations',
        'variations__sat_detail',
        'variations__service_detail',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceReadSerializer
        return ServiceWriteSerializer


# ── Service Bulk Update ───────────────────────────────────────────────────────

class ServiceBulkUpdateView(APIView):
    """
    Actualización integral de un Service (ProdServ) y sus variaciones.
    Cada variación envía un campo 'action': created, updated o deleted.

    PUT /services/<pk>/bulk-update/
    {
        "name": "Nuevo nombre",
        "clave_prod_serv": "01010101",
        "objeto_imp": "02",
        "variations": [
            {"action": "created", "base_price": "100.00", "service_detail": {...}, ...},
            {"action": "updated", "id": "<uuid>", "base_price": "120.00", ...},
            {"action": "deleted", "id": "<uuid>"}
        ]
    }
    """

    def put(self, request, pk):
        from django.db import transaction
        from invoicing.models.general import ProdServVariationSAT
        from invoicing.models.sat import ClaveUnidad, SatCatalog
        from .models import ServiceDetail

        try:
            service = ProdServ.objects.get(pk=pk)
        except ProdServ.DoesNotExist:
            return Response({'detail': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        variations_data = data.pop('variations', None)
        clave_prod_serv = data.pop('clave_prod_serv', '')
        objeto_imp = data.pop('objeto_imp', '')
        service_fields = data

        result = {'service_updated': False, 'variations': {}}

        def resolve_sat_catalog(catalog, pk):
            if not pk:
                return None
            return SatCatalog.objects.filter(catalog=catalog, pk=pk).first()

        def create_sat_detail(sat_fields):
            clave_unidad_code = sat_fields.pop('clave_unidad', '')
            return ProdServVariationSAT.objects.create(
                clave_prod_serv_id=clave_prod_serv or None,
                objeto_imp=resolve_sat_catalog('c_ObjetoImp', objeto_imp),
                clave_unidad_id=clave_unidad_code or None,
                **sat_fields,
            )

        def create_service_detail(detail_fields):
            return ServiceDetail.objects.create(**detail_fields)

        def extract_sat_fields(item):
            return {
                'clave_unidad': item.pop('clave_unidad', ''),
                'unidad': item.pop('unidad', ''),
            }

        def extract_service_detail_fields(item):
            detail = item.pop('service_detail', {}) or {}
            return {
                'billing_type': detail.get('billing_type', 'fixed'),
                'recurrence_every': detail.get('recurrence_every', 1),
                'recurrence_period': detail.get('recurrence_period', 'month'),
            }

        with transaction.atomic():
            # ── Update Service fields ──
            if service_fields:
                for attr, value in service_fields.items():
                    setattr(service, attr, value)
                service.save()
                result['service_updated'] = True

            # ── Process variations ──
            if variations_data is not None:
                created = []
                updated = []
                deleted = []

                for item in variations_data:
                    action = item.pop('action')
                    item_id = item.pop('id', None)
                    sat_fields = extract_sat_fields(item)
                    detail_fields = extract_service_detail_fields(item)

                    if action == 'created':
                        sat_detail = create_sat_detail(sat_fields)
                        service_detail = create_service_detail(detail_fields)
                        obj = ProdServVariation.objects.create(
                            product=service,
                            sat_detail=sat_detail,
                            service_detail=service_detail,
                            **item,
                        )
                        created.append(str(obj.id))

                    elif action == 'updated':
                        try:
                            variation = ProdServVariation.objects.get(id=item_id, product=service)
                        except ProdServVariation.DoesNotExist:
                            continue

                        # Update SAT detail
                        if variation.sat_detail:
                            clave_unidad_code = sat_fields.pop('clave_unidad', '')
                            update_kwargs = {'unidad': sat_fields.get('unidad', '')}
                            update_kwargs['clave_prod_serv_id'] = clave_prod_serv or variation.sat_detail.clave_prod_serv_id
                            objeto_imp_instance = resolve_sat_catalog('c_ObjetoImp', objeto_imp)
                            update_kwargs['objeto_imp'] = objeto_imp_instance if objeto_imp_instance else variation.sat_detail.objeto_imp
                            clave_unidad_instance = ClaveUnidad.objects.filter(clave=clave_unidad_code).first()
                            update_kwargs['clave_unidad'] = clave_unidad_instance if clave_unidad_instance else variation.sat_detail.clave_unidad
                            ProdServVariationSAT.objects.filter(id=variation.sat_detail_id).update(**update_kwargs)
                        else:
                            variation.sat_detail = create_sat_detail(sat_fields)

                        # Update or create ServiceDetail
                        if variation.service_detail:
                            ServiceDetail.objects.filter(id=variation.service_detail_id).update(**detail_fields)
                        else:
                            variation.service_detail = create_service_detail(detail_fields)

                        # Update variation fields
                        for attr, value in item.items():
                            setattr(variation, attr, value)
                        variation.save()
                        updated.append(str(item_id))

                    elif action == 'deleted':
                        ProdServVariation.objects.filter(id=item_id, product=service).delete()
                        deleted.append(str(item_id))

                result['variations'] = {'created': created, 'updated': updated, 'deleted': deleted}

        return Response(result, status=status.HTTP_200_OK)


# ── Service Variation ─────────────────────────────────────────────────────────

class ServiceVariationListCreateView(generics.ListCreateAPIView):
    queryset = ProdServVariation.objects.select_related(
        'product',
        'sat_detail',
        'sat_detail__clave_prod_serv',
        'sat_detail__clave_unidad',
        'sat_detail__objeto_imp',
        'service_detail',
    )
    search_fields = ['override_name']
    filterset_fields = ['product', 'is_active']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceVariationReadSerializer
        return ServiceVariationSerializer


class ServiceVariationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProdServVariation.objects.select_related(
        'product',
        'sat_detail',
        'sat_detail__clave_prod_serv',
        'sat_detail__clave_unidad',
        'sat_detail__objeto_imp',
        'service_detail',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ServiceVariationReadSerializer
        return ServiceVariationSerializer


# ── PriceList ───────────────────────────────────────────────────────────────────────────

class PriceListListCreateView(generics.ListCreateAPIView):
    queryset = PriceList.objects.prefetch_related('items__variant')
    serializer_class = PriceListSerializer
    search_fields = ['name']
    filterset_fields = ['currency', 'is_active']


class PriceListRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PriceList.objects.prefetch_related('items__variant')
    serializer_class = PriceListSerializer


# ── PriceListItem ───────────────────────────────────────────────────────────────────────

class PriceListItemListCreateView(generics.ListCreateAPIView):
    queryset = PriceListItem.objects.select_related('price_list', 'variant')
    serializer_class = PriceListItemSerializer
    filterset_fields = ['price_list', 'variant', 'is_active']


class PriceListItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PriceListItem.objects.select_related('price_list', 'variant')
    serializer_class = PriceListItemSerializer


# ── Product Dashboard ─────────────────────────────────────────────────────────

class ProductDashboardView(APIView):
    """Aggregated metrics for ProdServ / ProdServVariation dashboard."""

    def get(self, request, *args, **kwargs):
        total_products = ProdServ.objects.count()

        type_counts_qs = (
            ProdServ.objects
            .values('product_type__name')
            .annotate(count=models.Count('id'))
        )
        type_counts_map = {
            (row['product_type__name'] or '').lower(): row['count']
            for row in type_counts_qs
        }
        services_count = type_counts_map.get('servicio', 0)
        inventory_count = type_counts_map.get('inventario', 0)

        by_category_qs = (
            ProdServ.objects
            .values('category__name')
            .annotate(count=models.Count('id'))
            .order_by('category__name')
        )
        by_category = [
            {
                'name': row['category__name'] or 'Sin categoría',
                'count': row['count'],
            }
            for row in by_category_qs
        ]

        return Response({
            'total_products': total_products,
            'by_product_type': {
                'servicio': services_count,
                'inventario': inventory_count,
            },
            'by_category': by_category,
        }, status=status.HTTP_200_OK)

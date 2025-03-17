from pathlib import Path

from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import FileResponse
from django.http import HttpResponseNotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import parsers
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from beanserver.backend import models
from beanserver.backend.api import serializers as bean_serializers
from beanserver.backend.filters import BudgetFilter
from beanserver.backend.filters import CategoryFilter
from beanserver.backend.filters import TransactionGroupFilter

delete_permission_denied_msg = "You do not have permission to delete this object"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if "no_page" in request.query_params:
            return None

        return super().paginate_queryset(queryset, request, view)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = models.Budget.objects.all()
    serializer_class = bean_serializers.BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BudgetFilter
    ordering_fields = ["start_date", "end_date"]
    ordering = ["-start_date"]

    def get_queryset(self):
        queryset = self.queryset.filter(owner=self.request.user)
        return queryset.order_by(
            self.request.query_params.get("ordering", "-start_date"),
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)


class BudgetItemViewSet(viewsets.ModelViewSet):
    queryset = models.BudgetItem.objects.all()
    serializer_class = bean_serializers.BudgetItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = bean_serializers.TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = bean_serializers.CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = CategoryFilter
    search_fields = [
        "name",
        "description",
    ]
    ordering_fields = ["name"]
    ordering = ["name"]

    def create(self, request, *args, **kwargs):
        # To Support Bulk Creation
        serializer = self.get_serializer(
            data=request.data,
            many=isinstance(request.data, list),
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get_queryset(self):
        queryset = self.queryset.filter(owner=self.request.user)
        return queryset.order_by(
            self.request.query_params.get("ordering", "name"),
            "name",
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)


class TransactionGroupViewSet(viewsets.ModelViewSet):
    queryset = models.TransactionGroup.objects.all()
    serializer_class = bean_serializers.TransactionGroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TransactionGroupFilter
    ordering_fields = ["date"]
    ordering = ["-date"]
    search_fields = [
        "name",
        "description",
        "transactions__description",
        "transactions__name",
    ]

    def get_queryset(self):
        queryset = self.queryset.filter(owner=self.request.user)
        category_uuid = self.request.query_params.get("category_uuid")
        if category_uuid:
            queryset = queryset.filter(
                transactions__category_id=category_uuid,
            ).distinct()
            self.serializer_class.Meta.fields = [
                *self.serializer_class.Meta.fields,
                "transactions",
            ]
            self.serializer_class.transactions = bean_serializers.TransactionSerializer(
                many=True,
                read_only=True,
                source="transactions",
            )
        return queryset.order_by(self.request.query_params.get("ordering", "-date"))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset(),
        )  # Apply filters before calculating totals

        # Calculate income and expense before pagination
        totals = queryset.aggregate(
            income=Coalesce(
                Sum(
                    F("transactions__amount") * -1,
                    filter=Q(transactions__amount__lt=0),
                ),
                Value(0),
                output_field=DecimalField(),
            ),
            expense=Coalesce(
                Sum("transactions__amount", filter=Q(transactions__amount__gte=0)),
                Value(0),
                output_field=DecimalField(),
            ),
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

        else:  # no pagination
            serializer = self.get_serializer(queryset, many=True)
            return Response({"results": serializer.data, "totals": totals})

        response.data["totals"] = totals  # Add totals to the response
        return response

    def get_serializer_class(
        self,
    ):  # Override get_serializer_class for category filtering
        category_uuid = self.request.query_params.get("category_uuid")
        if (
            self.action in ("list", "retrieve") and category_uuid
        ):  # Only for GET requests with filtering

            class FilteredTransactionGroupSerializer(serializers.ModelSerializer):
                transactions = serializers.SerializerMethodField()

                class Meta(self.serializer_class.Meta):
                    # Don't need to do anything here. Fields are in the parent meta
                    pass

                def get_transactions(self, obj):
                    transactions = obj.transactions.filter(category_id=category_uuid)
                    return bean_serializers.TransactionSerializer(
                        transactions,
                        many=True,
                        context=self.context,
                    ).data

            return FilteredTransactionGroupSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)


# TODO: Add bulk create support for creating images alongside document scan
class DocumentScanViewSet(viewsets.ModelViewSet):
    queryset = models.DocumentScan.objects.all()
    serializer_class = bean_serializers.DocumentScanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)


# TODO: Add bulk create support
class ImageViewSet(viewsets.ModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = bean_serializers.ImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    parser_classes = (parsers.MultiPartParser,)
    # We don't need to update images
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        source = models.DocumentScan.objects.get(id=self.request.data.get("source"))
        serializer.save(owner=self.request.user, source=source)

    def retrieve(self, request, pk=None):
        try:
            image = self.get_queryset().get(pk=pk)
        except models.Image.DoesNotExist:
            return HttpResponseNotFound()
        return FileResponse(Path.open(image.image.path, "rb"), content_type="image/*")

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        if instance.image:
            file_path = Path(instance.image.path)
            if file_path.is_file():
                file_path.unlink()
        super().perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

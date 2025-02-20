from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from beanserver.backend import models
from beanserver.backend.api import serializers
from beanserver.backend.filters import BudgetFilter
from beanserver.backend.filters import CategoryFilter
from beanserver.backend.filters import TransactionGroupFilter

delete_permission_denied_msg = "You do not have permission to delete this object"


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = models.Budget.objects.all()
    serializer_class = serializers.BudgetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
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
    serializer_class = serializers.BudgetItemSerializer
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
    serializer_class = serializers.TransactionSerializer
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
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CategoryFilter

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
        return self.queryset.filter(owner=self.request.user).order_by(
            "legacy",
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
    serializer_class = serializers.TransactionGroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TransactionGroupFilter
    ordering_fields = ["date"]
    ordering = ["-date"]

    def get_queryset(self):
        queryset = self.queryset.filter(owner=self.request.user)
        return queryset.order_by(self.request.query_params.get("ordering", "-date"))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied(delete_permission_denied_msg)
        return super().perform_destroy(instance)

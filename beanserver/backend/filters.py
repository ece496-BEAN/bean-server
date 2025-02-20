from django_filters import rest_framework as filters

from beanserver.backend import models


class TransactionGroupFilter(filters.FilterSet):
    date_before = filters.DateFilter(field_name="date", lookup_expr="lte")
    date_after = filters.DateFilter(field_name="date", lookup_expr="gte")

    class Meta:
        model = models.TransactionGroup
        fields = ["date_before", "date_after"]


class BudgetFilter(filters.FilterSet):
    start_date_before = filters.DateFilter(field_name="start_date", lookup_expr="lte")
    start_date_after = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date_before = filters.DateFilter(field_name="end_date", lookup_expr="lte")
    end_date_after = filters.DateFilter(field_name="end_date", lookup_expr="gte")

    class Meta:
        model = models.Budget
        fields = [
            "start_date_before",
            "start_date_after",
            "end_date_before",
            "end_date_after",
        ]


class CategoryFilter(filters.FilterSet):
    class Meta:
        model = models.Category
        fields = {
            "legacy": ["exact"],
            "name": ["exact", "icontains"],
        }

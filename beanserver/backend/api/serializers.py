from rest_framework import serializers

from beanserver.backend.models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ["id", "category", "limit"]

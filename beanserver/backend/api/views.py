from rest_framework import generics

from beanserver.backend.api.serializers import BudgetSerializer
from beanserver.backend.models import Budget


class BudgetList(generics.ListCreateAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

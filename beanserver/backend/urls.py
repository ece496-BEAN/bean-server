from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from beanserver.backend.api import views

urlpatterns = [
    path("budgets/", views.BudgetList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

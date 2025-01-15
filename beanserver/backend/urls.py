from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from beanserver.backend.api import views

router = DefaultRouter()
router.register(r"transactions", views.TransactionViewSet)
router.register(r"transaction-groups", views.TransactionGroupViewSet)
router.register(r"categories", views.CategoryViewSet)
router.register(r"budgets", views.BudgetViewSet)

urlpatterns = [path("", include(router.urls))]
urlpatterns = format_suffix_patterns(urlpatterns)

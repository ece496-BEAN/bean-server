from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from beanserver.backend.api import views

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register(r"transactions", views.TransactionViewSet)
router.register(r"transaction-groups", views.TransactionGroupViewSet)
router.register(r"categories", views.CategoryViewSet)
router.register(r"budgets", views.BudgetViewSet)

app_name = "api"
urlpatterns = [path("", include(router.urls))]

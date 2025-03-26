from django.urls import path

from beanserver.users.api.views import UserDetailAPIView
from beanserver.users.api.views import UserPasswordUpdateAPIView
from beanserver.users.api.views import UserRegisterAPIView

app_name = "users"
urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("<uuid:id>/", UserDetailAPIView.as_view(), name="user-details"),
    path(
        "password/update/",
        UserPasswordUpdateAPIView.as_view(),
        name="user-password-update",
    ),
]

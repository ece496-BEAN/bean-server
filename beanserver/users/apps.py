import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "beanserver.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import beanserver.users.signals  # noqa: F401

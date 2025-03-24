from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "beanserver.backend"

    def ready(self):
        from beanserver.backend.api.signals import image_delete  # noqa: F401

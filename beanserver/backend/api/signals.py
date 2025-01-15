from typing import Any

from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver

from beanserver.backend.models import Category


@receiver(pre_delete, sender=Category)
def category_pre_delete(
    sender: type[Category],
    instance: Category,
    **kwargs: Any,
) -> None:
    if instance.budget_items.exists() or instance.transactions.exists():
        instance.legacy = True
        instance.save()


@receiver(pre_save, sender=Category)
def category_pre_save(sender, instance, **kwargs):
    # Check if the category name exists and the original is legacy
    try:
        original_category = Category.objects.get(name=instance.name)
        if original_category.id != instance.id and original_category.legacy:
            # Set legacy flag for the new instance
            instance.legacy = True
    except Category.DoesNotExist:
        pass  # Ignore if the original category doesn't exist

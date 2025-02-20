from pathlib import Path

from django.db.models.signals import post_delete
from django.dispatch import receiver

from beanserver.backend.models import Image


# TODO: Add support for AWS S3 storage
@receiver(post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Image` object is deleted.
    """
    if instance.image:  # Check if image file exists
        if Path.isfile(
            instance.image.path,
        ):  # Ensure it's a file and not a broken link
            Path.unlink(instance.image.path)

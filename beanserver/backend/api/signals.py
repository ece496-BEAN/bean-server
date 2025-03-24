from pathlib import Path

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from beanserver.backend import models


@receiver(pre_delete, sender=models.Image)
def image_delete(sender, instance, **kwargs):
    """
    Deletes the image file from the filesystem
    when the Image model instance is deleted.
    """
    if instance.image:
        file_path = Path(instance.image.path)
        if file_path.is_file():
            file_path.unlink()

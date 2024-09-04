# Create your models here.
from django.db import models


class Budget(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, blank=True, default="default_category")
    limit = models.FloatField(default=0.0)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return "TODO ADD"

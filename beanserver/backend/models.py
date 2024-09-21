# Create your models here.
import datetime
import uuid

from django.db import models
from django.utils import timezone

from beanserver.users.models import User


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.charField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True, default="")

    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(User, related_name="id", on_delete=models.CASCADE)

    # Date Range of the Budget
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self) -> str:
        return "TODO"

    def in_budget_time_period(self, date: datetime.datetime) -> bool:
        return self.start_date <= date <= self.end_date


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.charField(max_length=100, blank=False)
    description = models.CharField(max_length=255, blank=True, default="")
    # Set using `pre_delete` signal handlers
    legacy = models.BooleanField(default=False)
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(User, related_name="id", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "TODO"


class BudgetItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Don't allow deletion of categories in use
    # set to legacy instead for tracking purposes
    category_id = models.ForeignKey(
        Category,
        related_name="id",
        on_delete=models.RESTRICT,
    )
    budget_id = models.ForeignKey(Budget, related_name="id", on_delete=models.CASCADE)
    allocation = models.IntegerField()

    def __str__(self) -> str:
        return "TODO"


class DocumentScans(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ocr_result = models.TextField()  # Use TextField since this field can be very big
    ## TODO: (Figure out how to get this to work)
    invoice_image = models.ImageField(upload_to="images/")
    # Delete all user owned data when user is deleted
    # TODO: (Need to add a `post_delete` signal handler to delete the files as well)
    owner = models.ForeignKey(User, related_name="id", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "TODO"


class TransactionGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False)
    description = models.CharField(max_length=255, blank=True, default="")
    # `null` means `manual` input
    source = models.ForeignKey(
        DocumentScans,
        related_name="id",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    # Use default instead of auto_now_add to allow date to be updated
    date = models.DateTimeField(
        default=timezone.now,
    )  # Use default instead of auto_now_add to allow date to be updated
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(User, related_name="id", on_delete=models.CASCADE)

    def __str__(self):
        return "TODO"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.ForeignKey(
        TransactionGroup,
        related_name="id",
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=100, blank=False)
    category = models.ForeignKey(Category, related_name="id", on_delete=models.RESTRICT)
    description = models.CharField(max_length=255, blank=True, default="")
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(User, related_name="id", on_delete=models.CASCADE)

    def __str__(self):
        return "TODO"

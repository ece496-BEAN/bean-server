# Create your models here.
import datetime
import uuid

from django.db import models
from django.utils import timezone

from beanserver.users.models import User


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, default="Default Budget Name")
    description = models.CharField(max_length=255, blank=True, default="")

    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="budget",
        on_delete=models.CASCADE,
        null=True,
    )

    # Date Range of the Budget (Forced to do this by the linter)
    start_date = models.DateTimeField(default=timezone.now().date().replace(day=1))
    end_date = models.DateTimeField(
        default=timezone.now().date().replace(day=1).replace(month=12, day=31)
        if timezone.now().date().month == 1
        else timezone.now().date().replace(month=timezone.now().date().month + 1, day=1)
        - datetime.timedelta(days=1),
    )

    def __str__(self) -> str:
        return "Budget: " + self.name

    def in_budget_time_period(self, date: datetime.datetime) -> bool:
        return self.start_date <= date <= self.end_date


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, name="Default Category")
    description = models.CharField(max_length=255, blank=True, default="")
    # Set using `pre_delete` signal handlers
    legacy = models.BooleanField(default=False)
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="category",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self) -> str:
        return "Category: " + self.name


class BudgetItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Don't allow deletion of categories in use
    # set to legacy instead for tracking purposes
    category_id = models.ForeignKey(
        Category,
        related_name="budget_items",
        on_delete=models.RESTRICT,
    )
    budget_id = models.ForeignKey(
        Budget,
        related_name="budget_items",
        on_delete=models.CASCADE,
    )
    allocation = models.IntegerField()
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="budget_items",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self) -> str:
        return "BudgetItem: " + self.category_id.name


class DocumentScans(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ocr_result = models.TextField()  # Use TextField since this field can be very big
    ## TODO: (Figure out how to get this to work)
    invoice_image = models.ImageField(upload_to="images/")
    # Delete all user owned data when user is deleted
    # TODO: (Need to add a `post_delete` signal handler to delete the files as well)
    owner = models.ForeignKey(
        User,
        related_name="doc_scans",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self) -> str:
        return "DocumentScan: " + self.id


class TransactionGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        blank=False,
        default="Default Transaction Group Name",
    )
    description = models.CharField(max_length=255, blank=True, default="")
    # `null` means `manual` input
    source = models.ForeignKey(
        DocumentScans,
        related_name="transaction_groups",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    # Use default instead of auto_now_add to allow date to be updated
    date = models.DateTimeField(
        default=timezone.now,
    )  # Use default instead of auto_now_add to allow date to be updated
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="transaction_groups",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return "TransactionGroup: " + self.name


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.ForeignKey(
        TransactionGroup,
        related_name="group",
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(default=0)
    name = models.CharField(
        max_length=100,
        blank=False,
        default="Default Transaction Name",
    )
    category = models.ForeignKey(
        Category,
        related_name="transactions",
        on_delete=models.RESTRICT,
    )
    description = models.CharField(max_length=255, blank=True, default="")
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="transactions",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return "Transaction: " + self.name

# Create your models here.
import datetime
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
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
        default=timezone.now()
        .date()
        .replace(month=timezone.now().date().month + 1, day=1)
        - datetime.timedelta(days=1),
    )

    def __str__(self) -> str:
        return "Budget: " + self.name

    def in_budget_time_period(self, date: datetime.datetime) -> bool:
        return self.start_date <= date <= self.end_date

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            error_message = (
                f"End date ({self.end_date}) must be after "
                f"start date ({self.start_date})."
            )
            raise ValidationError({"end_date": error_message})
        super().clean()


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, default="Default Category")
    description = models.CharField(max_length=255, blank=True, default="")
    is_income_type = models.BooleanField(default=False)
    # Set using `pre_delete` signal handlers
    legacy = models.BooleanField(default=False)
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="category",
        on_delete=models.CASCADE,
        null=True,
    )
    color = models.CharField(
        max_length=9,  # max_length to 9 to fit '#RRGGBBAA'
        default="#e74297bf",
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$",  # Allow 6 or 8 hex chars
                message="Color must be in #RRGGBB or #RRGGBBAA format",
            ),
        ],
    )

    class Meta:
        # Ensure that the owner and name are unique together
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_owner_category_name",
            ),
        ]

    def __str__(self) -> str:
        return "Category: " + self.name

    # Custom delete method to prevent deletion of categories that are in use
    def delete(self, *args, **kwargs):
        if self.budget_items.exists() or self.transactions.exists():
            self.legacy = True  # Set to legacy instead of deleting
            self.save()
            return
        super().delete(*args, **kwargs)  # Proceed with deletion if no related objects


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
    allocation = models.DecimalField(decimal_places=2, default=0, max_digits=12)
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="budget_items",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        # Ensure that the each budget instance can't have a duplicate category
        constraints = [
            models.UniqueConstraint(
                fields=["category_id", "budget_id"],
                name="budget_unique_category",
            ),
        ]

    def __str__(self) -> str:
        return "BudgetItem: " + self.category_id.name


class DocumentScan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ocr_result = models.TextField()  # Use TextField since this field can be very big
    # Delete all user owned data when user is deleted
    owner = models.ForeignKey(
        User,
        related_name="doc_scans",
        on_delete=models.CASCADE,
        null=False,
    )

    def __str__(self) -> str:
        return "DocumentScan: " + self.id


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="images/")
    source = models.ForeignKey(
        DocumentScan,
        related_name="images",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    owner = models.ForeignKey(
        User,
        related_name="images",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self) -> str:
        return "Image: " + self.id


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
        DocumentScan,
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
        related_name="transactions",
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(decimal_places=2, default=0, max_digits=12)
    name = models.CharField(
        max_length=100,
        blank=False,
        default="Default Transaction Name",
    )
    category_id = models.ForeignKey(
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

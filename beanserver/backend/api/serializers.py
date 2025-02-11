from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from beanserver.backend import models


class BudgetItemSerializer(serializers.ModelSerializer):
    # Used for bulk updating via nested serializers
    uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
    )  # Writable ID field

    # TODO: add writable category_id field (need to add error handling as well 4
    # for updating to non-existent or non-owned categories)

    class Meta:
        model = models.BudgetItem
        fields = ["id", "uuid", "category_id", "budget_id", "allocation"]
        read_only_fields = ["id"]
        # If group_id is not set at all, it'll be caught by
        # the NOT NULL requirement in the database
        extra_kwargs = {"budget_id": {"required": False}}

    def update(self, instance, validated_data):
        if instance.owner.id != self.context["request"].user.id:
            permission_denied_msg = (
                "You do not have permission to update this budget item."
            )
            raise PermissionDenied(permission_denied_msg)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BudgetSerializer(serializers.ModelSerializer):
    budget_items = BudgetItemSerializer(many=True, required=False)

    class Meta:
        model = models.Budget
        fields = ["id", "name", "description", "start_date", "end_date", "budget_items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        budget_items_data = validated_data.pop("budget_items", [])

        with transaction.atomic():  # Use atomic transactions for data consistency
            new_budget = models.Budget.objects.create(
                **validated_data,
            )
            if budget_items_data:
                data = [
                    models.BudgetItem(
                        budget_id=new_budget,
                        owner=self.context["request"].user,
                        **transaction_data,
                    )
                    for transaction_data in budget_items_data
                ]
                models.BudgetItem.objects.bulk_create(data)
        return new_budget

    def update(self, instance, validated_data):
        if instance.owner.id != self.context["request"].user.id:
            permission_denied_msg = "You do not have permission to update this budget."
            raise PermissionDenied(permission_denied_msg)

        budget_items_data = validated_data.pop("budget_items", [])
        with transaction.atomic():
            # Update Budget fields
            instance.name = validated_data.get("name", instance.name)
            instance.description = validated_data.get(
                "description",
                instance.description,
            )
            instance.start_date = validated_data.get("start_date", instance.start_date)
            instance.end_date = validated_data.get("end_date", instance.end_date)

            instance.save()

            newly_created_budget_items: list[models.BudgetItem] = []
            updated_budget_items: list[models.BudgetItem] = []
            # TODO: Need to add error handling as well for updating
            # to non-existent or non-owned categories
            # FIXME: Currently no field to update category_id

            for budget_item_data in budget_items_data:
                budget_item_id = budget_item_data.get("uuid", None)
                if budget_item_id:
                    try:
                        # Update existing budget item instance
                        budget_item_instance = instance.budget_items.get(
                            id=budget_item_id,
                        )
                        if budget_item_instance.owner != self.context["request"].user:
                            permission_denied_msg = (
                                "You do not have permission to update this budget item."
                            )
                            raise PermissionDenied(permission_denied_msg)
                        for attr, value in budget_item_data.items():
                            if attr not in ("group_id", "uuid"):
                                # Don't try to update the budget_id or uuid
                                setattr(budget_item_instance, attr, value)
                        updated_budget_items.append(budget_item_instance)
                    except models.BudgetItem.DoesNotExist as err:
                        error_msg = (
                            f"Budget Item {budget_item_id} "
                            f"not found in budget {instance}."
                        )
                        raise ValidationError(error_msg) from err
                else:
                    # Prevent group_id from being set by the user
                    budget_item_data.pop("budget_id", None)
                    newly_created_budget_items.append(
                        models.BudgetItem(
                            group_id=instance,
                            owner=self.context["request"].user,
                            **budget_item_data,
                        ),
                    )

                # Update budget items in bulk (assumes we don't change `budget_id`)
                # TODO: add category_id to the list of fields to update
                # (need to add error handling)
                models.BudgetItem.objects.bulk_update(
                    updated_budget_items,
                    ["allocation", "category_id"],
                )

                # Delete budget items that were not updated
                instance.budget_items.exclude(
                    id__in=[item.id for item in updated_budget_items],
                ).delete()
                # Create new transactions
                models.BudgetItem.objects.bulk_create(newly_created_budget_items)
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = ["owner"]

    def update(self, instance, validated_data):
        if instance.owner.id != self.context["request"].user.id:
            permission_denied_msg = (
                "You do not have permission to update this category."
            )
            raise PermissionDenied(permission_denied_msg)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    # Used for bulk updating via nested serializers
    uuid = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
    )  # Writable ID field

    class Meta:
        model = models.Transaction
        fields = ["id", "uuid", "group_id", "amount", "name", "category", "description"]
        read_only_fields = ["id"]
        # If group_id is not set at all, it'll be caught by
        # the NOT NULL requirement in the database
        extra_kwargs = {"group_id": {"required": False}}

    def update(self, instance, validated_data):
        if instance.owner.id != self.context["request"].user.id:
            permission_denied_msg = (
                "You do not have permission to update this transaction."
            )
            raise PermissionDenied(permission_denied_msg)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TransactionGroupSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, required=False)  # Nested serializer

    class Meta:
        model = models.TransactionGroup
        fields = ["id", "name", "description", "source", "date", "transactions"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        transactions_data = validated_data.pop("transactions", [])

        with transaction.atomic():  # Use atomic transactions for data consistency
            new_group = models.TransactionGroup.objects.create(
                **validated_data,
            )
            if transactions_data:
                data = [
                    models.Transaction(
                        group_id=new_group,
                        owner=self.context["request"].user,
                        **transaction_data,
                    )
                    for transaction_data in transactions_data
                ]
                models.Transaction.objects.bulk_create(data)
        return new_group

    def update(self, instance, validated_data):
        if instance.owner.id != self.context["request"].user.id:
            permission_denied_msg = (
                "You do not have permission to update this transaction group."
            )
            raise PermissionDenied(permission_denied_msg)

        transactions_data = validated_data.pop("transactions", [])
        with transaction.atomic():
            # Update TransactionGroup fields
            instance.name = validated_data.get("name", instance.name)
            instance.description = validated_data.get(
                "description",
                instance.description,
            )
            instance.source = validated_data.get("source", instance.source)
            instance.date = validated_data.get("date", instance.date)
            instance.save()

            newly_created_transactions: list[models.Transaction] = []
            updated_transactions: list[models.Transaction] = []

            for transaction_data in transactions_data:
                transaction_id = transaction_data.get("uuid", None)
                if transaction_id:
                    try:
                        # Update existing transaction
                        transaction_instance = instance.transactions.get(
                            id=transaction_id,
                        )
                        if transaction_instance.owner != self.context["request"].user:
                            permission_denied_msg = (
                                "You do not have permission to update this transaction."
                            )
                            raise PermissionDenied(permission_denied_msg)

                        for attr, value in transaction_data.items():
                            if attr not in ("group_id", "uuid"):
                                # Don't try to update the group_id or uuid
                                setattr(transaction_instance, attr, value)
                        updated_transactions.append(transaction_instance)
                    except models.Transaction.DoesNotExist as err:
                        error_msg = (
                            f"Transaction {transaction_id} "
                            f"not found in group {instance}."
                        )
                        raise ValidationError(error_msg) from err
                else:
                    # Prevent group_id from being set by the user
                    transaction_data.pop("group_id", None)
                    newly_created_transactions.append(
                        models.Transaction(
                            group_id=instance,
                            owner=self.context["request"].user,
                            **transaction_data,
                        ),
                    )

                # Update transactions in bulk (assumes we don't change `group_id`)
                models.Transaction.objects.bulk_update(
                    updated_transactions,
                    ["amount", "name", "category", "description"],
                )

                # Delete transactions that were not updated
                instance.transactions.exclude(
                    id__in=[item.id for item in updated_transactions],
                ).delete()
                # Create new transactions
                models.Transaction.objects.bulk_create(newly_created_transactions)
        return instance

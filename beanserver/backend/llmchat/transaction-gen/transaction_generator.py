# ruff: noqa: S311,E501,TRY301,PLR0912,BLE001,DTZ011,C901,PERF401,B904
import datetime
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Literal

# --- Type Aliases ---
type TransactionType = Literal["credit", "debit"]
type PaymentMethod = Literal["Cash", "Credit Card", "Debit Card", "Direct Deposit", "E-Transfer"]


class AccountType(Enum):
    """
    Enum for different types of accounts.
    """

    CASH = auto()
    CHEQUING = auto()
    SAVINGS = auto()
    CREDIT_CARD = auto()
    INVESTMENT = auto()


@dataclass
class Account:
    """
    Represents a financial account.
    """

    name: str
    type: AccountType
    starting_balance: float
    currency: str = "CAD"

    def __hash__(self):
        return hash(self.name)


# --- Transaction Event Class ---
@dataclass
class TransactionEvent:
    """
    Represents a type of transaction event that can occur.
    """

    category: str
    subcategory: str
    source: str
    amount_generator: Callable[[], float]  # Function to generate a random amount
    transaction_type: TransactionType
    payment_method: PaymentMethod
    account: Account
    probability: float = 1.0  # Probability of occurring on any given day (0.0 to 1.0)
    frequency: str | None = None  # 'one-time', 'daily', 'weekly', 'bi-weekly', 'monthly'
    # Function to check if the event should occur on a given date
    occurrence_check: Callable[[datetime.date], bool] | None = None


# --- Transfer Event Class ---
@dataclass
class TransferEvent:
    """
    Represents a transfer of funds between two accounts.
    """

    source_account: Account
    destination_account: Account
    amount_generator: Callable[[], float]
    probability: float = 1.0
    frequency: str | None = None
    occurrence_check: Callable[[datetime.date], bool] | None = None


# --- Transaction Generator Class ---
class TransactionGenerator:
    """
    Generates randomized but logical transaction data for a given time range.
    """

    def __init__(self, accounts: list[Account]):
        self.accounts: list[Account] = accounts
        self.transaction_events: list[TransactionEvent] = []
        self.transfer_events: list[TransferEvent] = []
        self.categories: set[str] = set()
        self.subcategories: set[tuple[str, str]] = set()  # Set of (category, subcategory) tuples
        self._validate_accounts()

    def _validate_accounts(self) -> None:
        """
        Validates the provided accounts.
        """
        if not self.accounts:
            msg = "At least one account must be provided."
            raise ValueError(msg)

    def register_category(self, category: str) -> None:
        """
        Registers a category.
        """
        if not category:
            msg = "Category cannot be empty."
            raise ValueError(msg)
        if category in self.categories:
            msg = f"Category '{category}' is already registered."
            raise ValueError(msg)
        self.categories.add(category)

    def register_subcategory(self, category: str, subcategory: str) -> None:
        """
        Registers a subcategory under a category.
        """
        if not category:
            msg = "Category cannot be empty."
            raise ValueError(msg)
        if not subcategory:
            msg = "Subcategory cannot be empty."
            raise ValueError(msg)
        if category not in self.categories:
            msg = f"Category '{category}' is not registered. Please register the category first."
            raise ValueError(msg)
        if (category, subcategory) in self.subcategories:
            msg = f"Subcategory '{subcategory}' under category '{category}' is already registered."
            raise ValueError(msg)
        self.subcategories.add((category, subcategory))

    def register_transaction_event(self, event: TransactionEvent) -> None:
        """
        Registers a transaction event with validation.
        """
        self._validate_transaction_event(event)  # Perform validation
        self.transaction_events.append(event)

    def _validate_transaction_event(self, event: TransactionEvent) -> None:
        """
        Validates a transaction event before registration.
        """
        # 1. Check if category and subcategory are registered
        if event.category not in self.categories:
            msg = f"Category '{event.category}' is not registered."
            raise ValueError(msg)
        if (event.category, event.subcategory) not in self.subcategories:
            msg = f"Subcategory '{event.subcategory}' is not registered under category '{event.category}'."
            raise ValueError(msg)

        # 2. Check amount generator
        try:
            amount = event.amount_generator()
            if not isinstance(amount, (int, float)):
                msg = "Amount generator must return a number (int or float)."
                raise TypeError(msg)
        except Exception as e:
            msg = f"Invalid amount generator: {e}"
            raise ValueError(msg)

        # 3. Check transaction type
        if event.transaction_type not in ("credit", "debit"):
            msg = f"Invalid transaction type: '{event.transaction_type}'. Must be 'credit' or 'debit'."
            raise ValueError(msg)

        # 4. Check payment method
        if event.payment_method not in ("Cash", "Credit Card", "Debit Card", "Direct Deposit", "E-Transfer"):
            msg = f"Invalid payment method: '{event.payment_method}'."
            raise ValueError(msg)

        # 5. Check account
        if event.account not in self.accounts:
            msg = f"Account '{event.account.name}' is not registered."
            raise ValueError(msg)

        # 6. Check probability
        if not 0.0 <= event.probability <= 1.0:
            msg = "Probability must be between 0.0 and 1.0."
            raise ValueError(msg)

        # 7. Check frequency
        valid_frequencies = ("one-time", "daily", "weekly", "bi-weekly", "monthly")
        if event.frequency is not None and event.frequency not in valid_frequencies:
            msg = f"Invalid frequency: '{event.frequency}'. Must be one of {valid_frequencies} or None."
            raise ValueError(
                msg,
            )

        # 8. Check occurrence_check (if provided)
        if event.occurrence_check is not None:
            try:
                result = event.occurrence_check(datetime.date.today())
                if not isinstance(result, bool):
                    msg = "Occurrence check function must return a boolean value."
                    raise TypeError(msg)
            except Exception as e:
                msg = f"Invalid occurrence check function: {e}"
                raise ValueError(msg)

        # 9. Additional checks based on account type and payment method
        if event.account.type == AccountType.CREDIT_CARD and event.transaction_type == "credit":
            if event.payment_method not in ("Direct Deposit", "E-Transfer"):
                msg = "Credit transactions to a credit card account typically occur via Direct Deposit or E-Transfer."
                raise ValueError(
                    msg,
                )
        if event.account.type == AccountType.CASH and event.payment_method != "Cash":
            msg = "Transactions involving a cash account must use 'Cash' as the payment method."
            raise ValueError(msg)

    def register_transfer_event(self, event: TransferEvent) -> None:
        """
        Registers a transfer event with validation.
        """
        self._validate_transfer_event(event)
        self.transfer_events.append(event)

    def _validate_transfer_event(self, event: TransferEvent) -> None:
        """
        Validates a transfer event before registration.
        """
        # 1. Check accounts
        if event.source_account not in self.accounts:
            msg = f"Source account '{event.source_account.name}' is not registered."
            raise ValueError(msg)
        if event.destination_account not in self.accounts:
            msg = f"Destination account '{event.destination_account.name}' is not registered."
            raise ValueError(msg)
        if event.source_account == event.destination_account:
            msg = "Source and destination accounts must be different for a transfer."
            raise ValueError(msg)

        # 2. Check amount generator
        try:
            amount = event.amount_generator()
            if not isinstance(amount, (int, float)):
                msg = "Amount generator must return a number (int or float)."
                raise TypeError(msg)
        except Exception as e:
            msg = f"Invalid amount generator: {e}"
            raise ValueError(msg)

        # 3. Check probability
        if not 0.0 <= event.probability <= 1.0:
            msg = "Probability must be between 0.0 and 1.0."
            raise ValueError(msg)

        # 4. Check frequency
        valid_frequencies = ("one-time", "daily", "weekly", "bi-weekly", "monthly")
        if event.frequency is not None and event.frequency not in valid_frequencies:
            msg = f"Invalid frequency: '{event.frequency}'. Must be one of {valid_frequencies} or None."
            raise ValueError(
                msg,
            )

        # 5. Check occurrence_check (if provided)
        if event.occurrence_check is not None:
            try:
                result = event.occurrence_check(datetime.date.today())
                if not isinstance(result, bool):
                    msg = "Occurrence check function must return a boolean value."
                    raise TypeError(msg)
            except Exception as e:
                msg = f"Invalid occurrence check function: {e}"
                raise ValueError(msg)

    def _generate_transfer_transactions(self, current_date: datetime.date) -> list[dict]:
        """
        Generates transfer transactions for the current date.
        """
        transactions: list[dict] = []
        for event in self.transfer_events:
            if (
                event.frequency in ("one-time", "daily")
                or event.frequency == "weekly"
                and current_date.weekday() == 0
                or event.frequency == "bi-weekly"
                and current_date.weekday() == 0
                and (current_date.day - 1) % 14 == 0
                or event.frequency == "monthly"
                and current_date.day == 1
                or event.occurrence_check
                and event.occurrence_check(current_date)
            ):
                if random.random() < event.probability:
                    amount = event.amount_generator()
                    transactions.extend(
                        [
                            {
                                "date": current_date.isoformat(),
                                "category": "Transfer",
                                "subcategory": "Transfer Out",
                                "source": event.source_account.name,
                                "amount": amount,
                                "payment_method": "Internal Transfer",  # Add a new payment method for internal transfers
                                "account": event.source_account.name,
                                "transaction_type": "debit",
                            },
                            {
                                "date": current_date.isoformat(),
                                "category": "Transfer",
                                "subcategory": "Transfer In",
                                "source": event.destination_account.name,
                                "amount": amount,
                                "payment_method": "Internal Transfer",
                                "account": event.destination_account.name,
                                "transaction_type": "credit",
                            },
                        ],
                    )
        return transactions

    def generate_transactions(self, start_date: datetime.date, end_date: datetime.date) -> list[dict]:
        """
        Generates a list of transactions within the specified date range.
        """
        transactions: list[dict] = []

        # Add starting balances for accounts
        for account in self.accounts:
            transactions.append(
                {
                    "date": start_date.isoformat(),
                    "category": "Balance",
                    "subcategory": "Starting Balance",
                    "source": "Previous Period",
                    "amount": account.starting_balance,
                    "payment_method": "N/A",
                    "account": account.name,
                    "transaction_type": "credit" if account.starting_balance >= 0 else "debit",
                },
            )

        # Generate transactions for each day in the range
        current_date = start_date
        while current_date <= end_date:
            # Generate regular transactions
            for event in self.transaction_events:
                if event.frequency == "one-time" and current_date != start_date:
                    continue
                if (
                    event.frequency == "daily"
                    or (event.frequency == "weekly" and current_date.weekday() == 0)
                    or (
                        event.frequency == "bi-weekly"
                        and current_date.weekday() == 0
                        and (current_date - start_date).days % 14 == 0
                    )
                    or (event.frequency == "monthly" and current_date.day == 1)
                    or (event.occurrence_check and event.occurrence_check(current_date))
                ):
                    if random.random() < event.probability:
                        transactions.append(
                            {
                                "date": current_date.isoformat(),
                                "category": event.category,
                                "subcategory": event.subcategory,
                                "source": event.source,
                                "amount": event.amount_generator(),
                                "payment_method": event.payment_method,
                                "account": event.account.name,
                                "transaction_type": event.transaction_type,
                            },
                        )

            # Generate transfer transactions
            transactions.extend(self._generate_transfer_transactions(current_date))

            current_date += datetime.timedelta(days=1)

        return transactions

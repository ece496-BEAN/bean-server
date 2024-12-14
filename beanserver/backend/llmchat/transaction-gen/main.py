# ruff: noqa: S311,T201
import datetime
import random

from transaction_generator import Account
from transaction_generator import AccountType
from transaction_generator import TransactionEvent
from transaction_generator import TransactionGenerator
from transaction_generator import TransferEvent


def main():
    # 1. Define Accounts
    td_chequing = Account("TD Chequing", AccountType.CHEQUING, starting_balance=3000.00)
    bmo_savings = Account("BMO Savings", AccountType.SAVINGS, starting_balance=165.00)
    bmo_cc = Account("BMO CC", AccountType.CREDIT_CARD, starting_balance=-228.32)
    amazon_cc = Account("Amazon CC", AccountType.CREDIT_CARD, starting_balance=-111.43)
    cash_on_hand = Account("Cash on Hand", AccountType.CASH, starting_balance=500.00)

    # 2. Create a Transaction Generator
    accounts = [td_chequing, bmo_savings, bmo_cc, amazon_cc, cash_on_hand]
    generator = TransactionGenerator(accounts)

    # --- Register Categories and Subcategories ---
    # Income categories
    generator.register_category("Income")
    generator.register_subcategory("Income", "Salary/Wages")
    generator.register_subcategory("Income", "Dividends")
    generator.register_subcategory("Income", "Gift")

    # Expense categories
    generator.register_category("Expense")
    generator.register_subcategory("Expense", "Rent")
    generator.register_subcategory("Expense", "Groceries")
    generator.register_subcategory("Expense", "Utilities")

    # Transfer category
    generator.register_category("Transfer")
    generator.register_subcategory("Transfer", "Transfer In")
    generator.register_subcategory("Transfer", "Transfer Out")

    # 3. Register Transaction Events

    # --- Salary ---
    def biweekly_salary_amount():
        return round(random.uniform(2000, 2500), 2)

    salary_event = TransactionEvent(
        category="Income",
        subcategory="Salary/Wages",
        source="Walmart",
        amount_generator=biweekly_salary_amount,
        transaction_type="credit",
        payment_method="Direct Deposit",
        account=td_chequing,
        frequency="bi-weekly",
    )
    generator.register_transaction_event(salary_event)

    # --- Rent ---
    def monthly_rent_amount():
        return 1200.00

    rent_event = TransactionEvent(
        category="Expense",
        subcategory="Rent",
        source="ABC Apartments",
        amount_generator=monthly_rent_amount,
        transaction_type="debit",
        payment_method="E-Transfer",
        account=td_chequing,
        frequency="monthly",
    )
    generator.register_transaction_event(rent_event)

    # --- Groceries ---
    def groceries_amount():
        return round(random.uniform(20, 200), 2)

    groceries_event = TransactionEvent(
        category="Expense",
        subcategory="Groceries",
        source="Superstore",
        amount_generator=groceries_amount,
        transaction_type="debit",
        payment_method=random.choice(["Cash", "Credit Card", "Debit Card"]),
        account=random.choice([cash_on_hand, bmo_cc, amazon_cc, td_chequing]),
        probability=0.8,
        frequency="weekly",
    )
    generator.register_transaction_event(groceries_event)

    # --- Utilities ---
    def utilities_amount():
        return round(random.uniform(40, 150), 2)

    utilities_event = TransactionEvent(
        category="Expense",
        subcategory="Utilities",
        source="Bell",
        amount_generator=utilities_amount,
        transaction_type="debit",
        payment_method=random.choice(["Credit Card", "E-Transfer"]),
        account=random.choice([bmo_cc, amazon_cc, td_chequing]),
        probability=0.9,
        frequency="monthly",
    )
    generator.register_transaction_event(utilities_event)

    # --- Dividends ---
    def dividends_amount():
        return round(random.uniform(5, 25), 2)

    dividends_event = TransactionEvent(
        category="Income",
        subcategory="Dividends",
        source="XEQT",
        amount_generator=dividends_amount,
        transaction_type="credit",
        payment_method="Direct Deposit",
        account=bmo_savings,  # Assuming dividends go to savings
        frequency="monthly",
    )
    generator.register_transaction_event(dividends_event)

    # --- One-time Gift ---
    def gift_amount():
        return round(random.uniform(50, 500), 2)

    gift_event = TransactionEvent(
        category="Income",
        subcategory="Gift",
        source="Relative",
        amount_generator=gift_amount,
        transaction_type="credit",
        payment_method="Cash",
        account=cash_on_hand,
        frequency="one-time",
    )
    generator.register_transaction_event(gift_event)

    # --- Transfers ---
    def transfer_amount():
        return round(random.uniform(50, 500), 2)

    # Transfer from Chequing to Savings
    transfer_chequing_to_savings_event = TransferEvent(
        source_account=td_chequing,
        destination_account=bmo_savings,
        amount_generator=transfer_amount,
        probability=0.5,
        frequency="monthly",
    )
    generator.register_transfer_event(transfer_chequing_to_savings_event)

    # 4. Generate Transactions
    start_date = datetime.date(2024, 1, 1)
    end_date = datetime.date(2024, 1, 31)
    transactions = generator.generate_transactions(start_date, end_date)

    # 5. Print Transactions (Optional)
    for transaction in transactions:
        print(transaction)


if __name__ == "__main__":
    main()

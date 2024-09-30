from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from datetime import datetime

from dateutil.rrule import rrule
from pydantic import BaseModel
from pydantic import ConfigDict

Dollar = float
Description = str
Day = int


class Transaction(ABC, BaseModel):
    description: Description

    @abstractmethod
    def get_total_value(
        self,
        start_date: datetime,
        end_date: datetime,
        *,
        inc: bool = False,
    ) -> Dollar:
        pass

    @staticmethod
    def sum_total_values(
        transactions: Iterable["Transaction"],
        start_date: datetime,
        end_date: datetime,
        *,
        inc: bool = False,
    ) -> Dollar:
        return sum(t.get_total_value(start_date, end_date, inc=inc) for t in transactions)


class SingleTransaction(Transaction):
    transaction_value: Dollar
    transaction_date: datetime

    def get_total_value(
        self,
        start_date: datetime,
        end_date: datetime,
        *,
        inc: bool = False,
    ) -> Dollar:
        if inc:
            return (
                self.transaction_value
                if (self.transaction_date >= start_date and self.transaction_date <= end_date)
                else 0
            )
        return (
            self.transaction_value if (self.transaction_date > start_date and self.transaction_date < end_date) else 0
        )


class RecurringTransaction(Transaction):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """Note: the rrule class encompasses the frequency of the transaction (daily, monthly, etc.)"""
    frequency: rrule
    recurring_transaction_value: Dollar

    def get_total_value(
        self,
        start_date: datetime,
        end_date: datetime,
        *,
        inc: bool = False,
    ) -> Dollar:
        return self.recurring_transaction_value * len(
            self.frequency.between(start_date, end_date, inc),
        )

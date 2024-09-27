from abc import ABC
from abc import abstractmethod
from datetime import date

from dateutil.rrule import rrule
from pydantic import BaseModel
from pydantic import ConfigDict

Dollar = int
Description = str
Day = int


class Transaction(ABC, BaseModel):
    description: Description

    @abstractmethod
    def get_total_value(
        self,
        start_date: date,
        end_date: date,
        *,
        inc: bool = False,
    ) -> Dollar:
        pass


class MonthlyTransaction(Transaction):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    frequency: rrule
    monthly_transaction_value: Dollar

    def get_total_value(
        self,
        start_date: date,
        end_date: date,
        *,
        inc: bool = False,
    ) -> Dollar:
        return self.monthly_transaction_value * len(
            self.frequency.between(start_date, end_date, inc),
        )

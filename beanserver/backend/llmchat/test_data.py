# ruff: noqa

from datetime import datetime

from dateutil.rrule import MONTHLY
from dateutil.rrule import rrule
from transaction import MonthlyTransaction

budgets = [
    ["Groceries (all food and non-alcoholic drinks purchased for home)", 200],
    ["Dining & Takeout (restaurant meals, takeout, and coffee shops)", 200],
    ["Alcohol (alcoholic beverages from stores or restaurants)", 20],
    ["Rent or Mortgage", 1500],
    ["Utilities (electricity, gas, water, sanitation)", 0],
    ["Home Maintenance (repairs, cleaning services, household goods)", 50],
    ["Home Insurance", 0],
    ["Vehicle Purchase (new or used cars, trucks, etc.)", 0],
    ["Fuel (gas, diesel, electric charging)", 0],
    ["Vehicle Maintenance (repairs, parts, car washes)", 0],
    ["Public Transport (bus, train, subway)", 150],
    ["Parking & Tolls", 0],
    ["Airfare (flights)", 0],
    ["Other Transport Services (taxis, ride-shares, ferries)", 0],
    ["Clothing & Footwear", 300],
    ["Health & Wellness (pharmaceuticals, medical products, insurance, therapy)", 200],
    ["Grooming & Beauty (haircuts, skincare, makeup)", 25],
    ["Childcare", 0],
    ["Hobbies & Leisure (sports equipment, games, toys, outdoor recreation)", 200],
    ["Subscriptions (streaming services, digital content, magazines)", 60],
    ["Pets (food, veterinary care, grooming)", 0],
    ["Events & Activities (concerts, movies, gyms)", 80],
]

datetime_today = datetime(
    datetime.today().year,
    datetime.today().month,
    datetime.today().day,
)

budget_transactions = [
    MonthlyTransaction(
        description=cat[0],
        monthly_transaction_value=-1 * cat[1],
        frequency=rrule(MONTHLY, dtstart=datetime_today),
    )
    for cat in budgets
]

if __name__ == "__main__":
    print(sum(t.monthly_transaction_value for t in budget_transactions))
    print(
        sum(
            [
                t.get_total_value(
                    datetime_today,
                    datetime_today.replace(year=datetime_today.year + 1),
                    inc=True,
                )
                for t in budget_transactions
            ],
        ),
    )
    # print([t.frequency.between(date.today(), date(2030, 1, 1), inc=True)
    #       for t in budget_transactions])
    # print([t.frequency for t in budget_transactions])

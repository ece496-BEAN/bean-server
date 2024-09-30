# ruff: noqa
import itertools
from datetime import MINYEAR
from datetime import datetime
from datetime import timedelta

import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
from dash import Dash
from dash import Input
from dash import Output
from dash import callback
from dash import dcc
from dash import html
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, DAILY
from dateutil.rrule import rrule
from dateutil.utils import today
from transaction import RecurringTransaction
from transaction import SingleTransaction
from transaction import Transaction

datetime_today = datetime(
    datetime.today().year,
    datetime.today().month,
    datetime.today().day,
)
datetime_yesterday = datetime_today - timedelta(days=1)
datetime_transaction_start = datetime(
    datetime_today.year,
    datetime_today.month,
    1,
)

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


budget_transactions = [
    RecurringTransaction(
        description=cat[0],
        recurring_transaction_value=-1 * cat[1],
        frequency=rrule(MONTHLY, dtstart=datetime_transaction_start),
    )
    for cat in budgets
]

incomes = [
    ["Intel", 4000],
    ["TA UofT", 400],
    ["CASH.TO", 100],
]
income_transactions = [
    RecurringTransaction(
        description=cat[0],
        recurring_transaction_value=cat[1],
        frequency=rrule(MONTHLY, dtstart=datetime_transaction_start),
    )
    for cat in incomes
]


savings_transactions = [
    SingleTransaction(description=cat[0], transaction_value=cat[1], transaction_date=datetime_today)
    for cat in [["TD Chequing", 2000], ["TD Savings", 5000], ["WS Cash", 10000], ["WS TFSA", 15000]]
]

onetime_simple_purchase_goals = [
    # IMPORTANT: note the `- timedelta(days=1)` - this is because we we are calculating time
    # INCLUSIVE, so we need to have saved everything by the end date
    # e.g., if today Jan 1 and the end date is Jan 31, then I should be saving money from Jan 1 to Jan 31 inclusive.
    [
        "New Phone",
        rrule(
            DAILY,
            dtstart=datetime_transaction_start,
            until=datetime_transaction_start + relativedelta(years=1) - timedelta(days=1),
        ),
        1299.99,
    ],
    [
        "VR Headset",
        rrule(
            DAILY,
            dtstart=datetime_transaction_start,
            until=datetime_transaction_start + relativedelta(months=3) - timedelta(days=1),
        ),
        675.35,
    ],
    [
        "Vacation to Paris",
        rrule(
            DAILY,
            dtstart=datetime_transaction_start,
            until=datetime_transaction_start + relativedelta(months=15) - timedelta(days=1),
        ),
        13500,
    ],
]

onetime_simple_purchase_goals_transactions = [
    RecurringTransaction(description=goal[0], recurring_transaction_value=goal[2] / goal[1].count(), frequency=goal[1])
    for goal in onetime_simple_purchase_goals
]

all_transactions: [Transaction] = list(
    itertools.chain(
        budget_transactions, income_transactions, savings_transactions, onetime_simple_purchase_goals_transactions
    )
)

#########
date_query_range = rrule(MONTHLY, datetime_today)

dates = list(date_query_range.xafter(datetime_yesterday, 13))
savings_values = [
    Transaction.sum_total_values(
        all_transactions,
        datetime_yesterday,
        end_date,
        inc=True,
    )
    for end_date in dates
]
df = pd.DataFrame({"Date": dates, "Savings": savings_values})

toggle_column_defs = [{"field": "transaction"}, {"field": "enabled", "cellDataType": "boolean", "editable": True}]
row_data = [
    {
        "transaction": t.description,
        "enabled": True,
    }
    for t in all_transactions
]

app = Dash()
app.layout = [
    html.H1(children="Your Savings Graph", style={"textAlign": "center"}),
    dcc.Graph(id="graph-content", figure=px.line(df, x="Date", y="Savings")),
    dag.AgGrid(
        id="transaction-toggles",
        columnDefs=toggle_column_defs,
        rowData=row_data,
        defaultColDef={"editable": False},
        dashGridOptions={"animateRows": False},
    ),
]


@callback(Output("graph-content", "figure"), Input("transaction-toggles", "cellValueChanged"))
def update_graph(cell_changes):
    if cell_changes is not None:
        for cell_change in cell_changes:
            row_data[cell_change["rowIndex"]]["enabled"] = cell_change["data"]["enabled"]

    savings_values = [
        Transaction.sum_total_values(
            (t for (t, data) in zip(all_transactions, row_data, strict=True) if data["enabled"]),
            datetime_yesterday,
            end_date,
            inc=True,
        )
        for end_date in dates
    ]
    df = pd.DataFrame({"Date": dates, "Savings": savings_values})
    return px.line(df, x="Date", y="Savings")


if __name__ == "__main__":
    # print(sum(t.monthly_transaction_value for t in budget_transactions))
    # print(sum(t.monthly_transaction_value for t in income_transactions))

    # app.run(debug=True)
    app.run(debug=False)

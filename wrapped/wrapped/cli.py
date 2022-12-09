"""
Generates a breakdown of expenses over a year period.

Sparated into the following, which are measured against one another:

- Operating Income
- Bills
- Subscriptions
- Fun
  - Food
  - Vacation
  - Gifts
- Maintenance
- One Timers
"""

import typer
from message import Message, add_progress
import pandas as pd
from utils import session, BASE_URL

app = typer.Typer()
SESSION = session()
BUDGET = None

def get_budget():

    # List the available budgets
    budgets = SESSION.get(f"{BASE_URL}/budgets").json()['data']['budgets']

    selected_budget = Message(
        f"We found {len(budgets)} to analyze! 🚆🚆\nWhich would you like to chose? "
        "(Enter the number next to the name to select.)"
    ).choice([
        f"({i}) {b['name']}" for i, b in enumerate(budgets)
    ])
    selected_budget = budgets[int(selected_budget)]["id"]

    BUDGET = SESSION.get(f"{BASE_URL}/budgets/{selected_budget}")

def get_categories():

    budget = BUDGET.json()

    # https://api.youneedabudget.com/#deltas
    server_knowledge = budget["server_knowledge"]
    SESSION.params = {"last_knowledge_of_server": server_knowledge}

    categories = set(budget["data"]["budget"]["category_groups"])

    # Allow the user to select the categories to review in specific
    restricted_groups = set("Internal Master Category", "Hidden Categories")

    selected_categories = Message(
        f"We found {len(categories)} to analyze!\nWhich would you like to get reports on? "
        "(Enter the number next to the name to select, multiple selections should "
        "have spaces between them)\nType <A> to select all groups."
    ).choice([
        f"({i}) {b['name']}" for i, b in enumerate(categories - restricted_groups)
    ])

    if selected_categories.lower() == "a" or selected_categories.lower() == "<a>":
        selected_categories = categories
    else:
        selected_categories = {int(i) for i in selected_categories.split(" ")}
        selected_categories = [c for i, c in enumerate(categories) if i in selected_categories] 

    Message(
        f"Thanks! A review will be performed on {len(selected_categories)} categories!"
    ).info()

    return selected_categories


def get_years():

    # Get the years to review
    pass

def get_sub_categories():

    budget = BUDGET.json()

    # Get the category with the highest percent difference
    # Get the category with the lowest percent difference
    # Get the category with the highest difference
    # Get the category with the lowest difference


def percent_diff(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


def gather_data(initial, compared, init_year, comp_year):
    # - Operating Income
    report = f"Comparison of expenses for CY {init_year} - {comp_year}\n"
    # Get all of the categories that are the same across both years
    for category in (
        "Total Income",
        "Immediate Obligations",
        "True Expenses",
        "Groceries",
        "Medical 🏨",
        "Auto Maintenance 🚗",
        "Subscriptions",
        "Quality of Life Goals",
        "Vacation 🏝",
        "Gifts 🎁",
        "Just for Fun",
    ):
        init_total, comp_total = [
            r["Total"]
            for k in [initial, compared]
            for r in k
            if r["Category"] == category
        ]
        init_total, comp_total = abs(init_total), abs(comp_total)
        total_diff = comp_total - init_total

        report += f"""
        --- {category} {'✔️' if total_diff < 0 else ''} ---
        """
        report += f"""
        {init_year} Expense:{' '*8}${init_total:,.2f}
        {comp_year} Expense:{' '*8}${comp_total:,.2f}
        """
        report += f"""
        Difference:          ${comp_total - init_total:,.2f}
        Percent Difference:  %{percent_diff(init_total, comp_total):.2f}

        """
    return report

@app.command()
def run():
    initial_year = Message("Enter starting year (YYYY)").prompt()
    compared_year = Message("Enter comparison year (YYYY)").prompt()

    # Gather the coeesponding year docs
    init, comp = [
        pd.read_csv(f"../data/expense-reports/{y}-expense-report.csv")
         for y in [initial_year, compared_year]
    ]

    # Gather all of the data for the main expenditures
    report = gather_data(init.to_dict(orient="records"), comp.to_dict(orient="records"), initial_year, compared_year)
    
    response = Message("Report Generated, Save (y) or Print to Standard Output (n)").confirmation()

    if response:
        with open("report.txt", "w") as f:
            f.write(report)
    else:
        print(report)
def main():
    app()

if __name__ == "__main__":
    app()

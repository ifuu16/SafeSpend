# ===== finance.py =====
# Handles all financial data processing and affordability logic.
# No LLM involved — pure Python + pandas.

import pandas as pd


def load_transactions(filepath: str) -> pd.DataFrame:
    """Load and validate the CSV file."""
    try:
        df = pd.read_csv(filepath, parse_dates=["date"])
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")

    required_cols = {"date", "description", "amount", "category"}
    missing = required_cols - set(df.columns.str.lower())
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    df.columns = df.columns.str.lower()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df.dropna(subset=["amount"], inplace=True)
    return df


def compute_financial_summary(df: pd.DataFrame) -> dict:
    """
    Derive key financial metrics from transaction history.

    - Income:   positive amounts
    - Expenses: negative amounts (stored as negatives)
    - Balance:  sum of all transactions
    - Disposable income: total income + total expenses (expenses are negative)
    """

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    # Split into income and expense rows
    income_df = df[df["amount"] > 0]
    expense_df = df[df["amount"] < 0]

    # Determine how many months of data we have (at least 1)
    if df["date"].nunique() > 0:
        date_range_months = max(
            1,
            (df["date"].max() - df["date"].min()).days / 30.44
        )
    else:
        date_range_months = 1

    total_income = income_df["amount"].sum()
    total_expenses = expense_df["amount"].sum()          # negative value
    current_balance = df["amount"].sum()                 # net balance

    monthly_income = total_income / date_range_months
    monthly_expenses = abs(total_expenses) / date_range_months  # positive for display

    # Disposable income = what's left after expenses each month
    disposable_income = monthly_income - monthly_expenses

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(abs(total_expenses), 2),
        "current_balance": round(current_balance, 2),
        "monthly_income": round(monthly_income, 2),
        "monthly_expenses": round(monthly_expenses, 2),
        "disposable_income": round(disposable_income, 2),
        "months_of_data": round(date_range_months, 1),
    }


def evaluate_affordability(summary: dict, cost: float) -> dict:
    """
    Deterministic affordability decision — no LLM involved.

    Rules (in priority order):
      1. cost > current balance           → NO
      2. cost > 50% of disposable income  → CAUTION
      3. otherwise                        → YES
    """
    balance = summary["current_balance"]
    disposable = summary["disposable_income"]

    # Avoid division by zero
    pct_of_disposable = (cost / disposable * 100) if disposable > 0 else float("inf")

    if cost > balance:
        decision = "NO"
        reason = "Purchase exceeds your current balance."
    elif disposable <= 0:
        decision = "NO"
        reason = "You have no positive disposable income this month."
    elif pct_of_disposable > 50:
        decision = "CAUTION"
        reason = f"Purchase uses {pct_of_disposable:.1f}% of your monthly disposable income."
    else:
        decision = "YES"
        reason = f"Purchase uses only {pct_of_disposable:.1f}% of your monthly disposable income."

    remaining_balance = round(balance - cost, 2)

    return {
        "decision": decision,
        "reason": reason,
        "remaining_balance": remaining_balance,
        "pct_of_disposable": round(pct_of_disposable, 1),
    }
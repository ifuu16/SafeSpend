# ===== app.py =====
# Entry point for the Personal CFO CLI tool.
# Usage: python app.py --file data.csv --item "AirPods" --cost 250

import argparse
import sys

# Load .env file if present (requires python-dotenv; silently skipped if not installed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from finance import load_transactions, compute_financial_summary, evaluate_affordability
from agent import get_llm_explanation


def parse_args():
    parser = argparse.ArgumentParser(
        description="Personal CFO — Can I Afford This?"
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to your financial transactions CSV file"
    )
    parser.add_argument(
        "--item", required=True,
        help='Name of the item you want to buy (e.g. "AirPods")'
    )
    parser.add_argument(
        "--cost", required=True, type=float,
        help="Cost of the item in dollars (e.g. 250)"
    )
    return parser.parse_args()


def print_output(decision: str, llm_text: str):
    """Print the final structured output."""
    print("\n" + "=" * 50)
    print(f"Decision: {decision}")
    print("=" * 50)
    print(llm_text)
    print("=" * 50 + "\n")


def main():
    args = parse_args()

    # ── Step 1: Load and validate the CSV ──────────────────────────────────
    print(f"\nLoading transactions from: {args.file}")
    try:
        df = load_transactions(args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    print(f"  → {len(df)} transactions loaded.")

    # ── Step 2: Compute financial summary (pure Python / pandas) ───────────
    summary = compute_financial_summary(df)
    print(f"  → Balance: ¥{summary['current_balance']:,.2f} | "
          f"Disposable/mo: ¥{summary['disposable_income']:,.2f}")

    # ── Step 3: Deterministic affordability decision ───────────────────────
    result = evaluate_affordability(summary, args.cost)
    print(f"  → Affordability decision: {result['decision']} ({result['reason']})")

    # ── Step 4: LLM explanation ────────────────────────────────────────────
    print("\nAsking your Personal CFO for an explanation…")
    try:
        llm_text = get_llm_explanation(args.item, args.cost, summary, result)
    except EnvironmentError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        sys.exit(1)

    # ── Step 5: Print formatted output ────────────────────────────────────
    print_output(result["decision"], llm_text)


if __name__ == "__main__":
    main()
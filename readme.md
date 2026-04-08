# Personal CFO — "Can I Afford This?" Agent

A zero-cost, CLI-based affordability advisor powered by deterministic Python logic + Ollama AI.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run a query
python app.py --file data.csv --item "AirPods" --cost 250
```

## How It Works

| Step | Component | What it does |
|------|-----------|--------------|
| 1 | `finance.py` | Loads CSV, computes income / expenses / balance |
| 2 | `finance.py` | Applies rule-based decision: YES / CAUTION / NO |
| 3 | `agent.py`  | Sends summary to Claude for a plain-English explanation |
| 4 | `app.py`    | Prints the formatted result |

## Decision Rules (pure Python — no LLM)

| Condition | Decision |
|-----------|----------|
| cost > current balance | **NO** |
| cost > 50% of monthly disposable income | **CAUTION** |
| otherwise | **YES** |

## CSV Format

```
date,description,amount,category
2024-01-01,Salary,4500.00,Income
2024-01-05,Rent,-1200.00,Housing
```

- Positive = income
- Negative = expense

## Example Output

```
==================================================
Decision: CAUTION
==================================================
Summary:
Your finances show a healthy monthly income of $4,600 with moderate expenses...

Financial Impact:
- Remaining balance: $7,142.02
- Disposable income: $1,832.67
- % used: 54.3%

Advice:
Consider waiting until next month when...
==================================================
```
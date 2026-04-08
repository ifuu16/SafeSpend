# ===== agent.py =====
# Uses Ollama (local llm)

import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(item: str, cost: float, summary: dict, result: dict) -> str:
    return f"""You are a helpful personal financial advisor (CFO).
A user wants to know if they can afford a purchase. You have been given their financial summary
and a pre-computed decision. Your job is to explain the decision clearly and give actionable advice.

--- PURCHASE ---
Item: {item}
Cost: ¥{cost:,.2f}

--- FINANCIAL SUMMARY ---
Current Balance:        ¥{summary['current_balance']:,.2f}
Monthly Income:         ¥{summary['monthly_income']:,.2f}
Monthly Expenses:       ¥{summary['monthly_expenses']:,.2f}
Disposable Income/mo:   ¥{summary['disposable_income']:,.2f}
Months of Data:         {summary['months_of_data']}

--- DECISION (already computed — do NOT change it) ---
Decision:  {result['decision']}
Reason:    {result['reason']}
Remaining Balance After Purchase: ¥{result['remaining_balance']:,.2f}
% of Disposable Income Used:      {result['pct_of_disposable']}%

--- IMPORTANT CONTEXT ---
The user is trying to build financial stability over time.
Always consider:
- Emergency savings (3–6 months of expenses)
- Ability to handle unexpected costs
- Impact on future purchases or goals
- Whether this is a recurring behavior

--- YOUR TASK ---
Write a response in EXACTLY this format (no extra sections):

Summary:
<2–3 sentences summarising the user's financial situation and whether the purchase is wise>

Financial Impact:
- Remaining balance: ¥{result['remaining_balance']:,.2f}
- Disposable income: ¥{summary['disposable_income']:,.2f}
- % used: {result['pct_of_disposable']}%

Future Impact:
<2–3 sentences explaining the long-term consequence of this purchase. 
Consider savings growth, emergency buffer, and ability to afford future goals. 
Be specific and realistic.>

Advice:
<2–4 sentences of concrete, empathetic financial advice>

--- TONE RULE ---
Always speak directly to the user using "you" and "your".
Do NOT refer to "the user".
Make the response feel personal, like a financial advisor speaking directly to a client.
Keep the tone friendly and professional. Do not repeat the decision label — it will be printed separately.
"""



def get_llm_explanation(item: str, cost: float, summary: dict, result: dict) -> str:
    prompt = build_prompt(item, cost, summary, result)

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast + cheap
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
import streamlit as st
from finance import load_transactions, compute_financial_summary, evaluate_affordability
from agent import get_llm_explanation
import pandas as pd

st.set_page_config(page_title="Personal CFO", layout="centered")

st.title("💴 💹 SAFESPEND")
st.caption("Make smarter spending decisions instantly")

tab1, tab2, tab3 = st.tabs(["🛍️ Decision", "📊 Dashboard", "💬 Feedback"
 ])

with tab3:
    st.subheader("💬 Help Us Improve.\n We'd appreciate your Honest Feedback")

    st.markdown("Takes a minute👇")

    feedback = st.text_area("What confused you or could be better?")

    rating = st.slider("How useful is this app?", 1, 5, 3)

    if st.button("Submit Feedback"):
        st.success("Thanks! 🙌")

# --- Input Section ---
with tab1:
    st.subheader("🛍️ Purchase Decision")

    summary = None
    uploaded_file = None

    input_mode = st.radio(
    "Choose how to provide your financial data:",
    ["📁 Upload CSV", "⚡ Enter Manually"],
    index=1
    )

    # ===== CSV MODE =====
    if input_mode == "📁 Upload CSV":
        uploaded_file = st.file_uploader("Upload your transactions", type=["csv"])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            summary = compute_financial_summary(df)
            st.success("File loaded ✅")

# ===== MANUAL MODE =====
    elif input_mode == "⚡ Enter Manually":
        st.markdown("### Add Transactions")

    with st.form("manual_transaction_form"):
        desc = st.text_input("Description: What is this for?")

        amount = st.number_input("Amount (¥)", value=0.0)
        t_type = st.selectbox("Type", ["Expense", "Income"])
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Other"])
        date = st.date_input("Date")

        submitted = st.form_submit_button("Add Transaction")

    if submitted:
        transaction = {
            "description": desc,
            "amount": amount if t_type == "Income" else -amount,
            "category": category,
            "date": pd.to_datetime(date)
        }

        st.session_state.setdefault("manual_transactions", [])
        st.session_state["manual_transactions"].append(transaction)

        st.success("Transaction added ✅")

    # Build summary from saved transactions
    if "manual_transactions" in st.session_state and len(st.session_state["manual_transactions"]) > 0:
        df = pd.DataFrame(st.session_state["manual_transactions"])
        summary = compute_financial_summary(df)

        st.markdown("### Your Transactions")
        st.dataframe(df)
    else:
        summary = None

    
    item = st.text_input("What do you want to buy?")
    cost = st.number_input("Cost (¥)", value=0.0)

    if st.button("Can I afford this?"):

        # ===== VALIDATION =====
        if not item or cost <= 0:
            st.warning("Enter a valid item and cost.")
            st.stop()

        # ===== BUILD SUMMARY BASED ON MODE =====
        if input_mode == "📁 Upload CSV":

            if uploaded_file is None:
                st.warning("Please upload a CSV file.")
                st.stop()

            df = load_transactions(uploaded_file)

            if "manual_expenses" in st.session_state:
                manual_df = pd.DataFrame(st.session_state["manual_expenses"])
                df = pd.concat([df, manual_df], ignore_index=True)

            summary = compute_financial_summary(df)

            expense_df = df[df["amount"] < 0].copy()
            expense_df["amount"] = expense_df["amount"].abs()
            category_spending = expense_df.groupby("category")["amount"].sum()

        else:  # ⚡ MANUAL MODE

            if "manual_transactions" not in st.session_state or len(st.session_state["manual_transactions"]) == 0:
                st.warning("Please add at least one transaction.")
                st.stop()

            df = pd.DataFrame(st.session_state["manual_transactions"])
            summary = compute_financial_summary(df)

            expense_df = df[df["amount"] < 0].copy()
            expense_df["amount"] = expense_df["amount"].abs()
            category_spending = expense_df.groupby("category")["amount"].sum()

        # ===== DECISION =====
        result = evaluate_affordability(summary, cost)

        chart_data = pd.DataFrame({
            "Type": ["Income", "Expenses"],
            "Amount": [summary["monthly_income"], summary["monthly_expenses"]]
        }).set_index("Type")

        # ===== STORE =====
        st.session_state["summary"] = summary
        st.session_state["result"] = result
        st.session_state["category_spending"] = category_spending
        st.session_state["chart_data"] = chart_data
        st.session_state["item"] = item
        st.session_state["cost"] = cost
with tab2:
    st.subheader("📊 Financial Overview")

    if "summary" not in st.session_state:
        st.info("Run a decision first 👈")
    else:
        summary = st.session_state["summary"]
        result = st.session_state["result"]
        category_spending = st.session_state["category_spending"]
        chart_data = st.session_state["chart_data"]
        item = st.session_state["item"]
        cost = st.session_state["cost"]

        col1, col2, col3 = st.columns(3)

        col1.metric("Balance", f"¥{summary['current_balance']:,.0f}")
        col2.metric("Income", f"¥{summary['monthly_income']:,.0f}")
        col3.metric("Disposable", f"¥{summary['disposable_income']:,.0f}")

        st.subheader("📊 Spending Breakdown")
        st.bar_chart(category_spending)

        st.subheader("💴 Income vs Expenses")
        st.bar_chart(chart_data)

        # --- Decision ---
        st.subheader("🧠 Decision")

        if result["decision"] == "YES":
            st.success("✅ YES — You can afford this")
        elif result["decision"] == "CAUTION":
            st.warning("⚠️ CAUTION — Think twice")
        else:
            st.error("❌ NO — Not affordable")

        # --- AI Explanation ---
        st.subheader("💬 What This Means for You")

        with st.spinner("Analyzing your finances..."):
            explanation = get_llm_explanation(item, cost, summary, result)

        st.write(explanation)



# -----------------------------
# trip_test1.py
# -----------------------------
import streamlit as st
st.set_page_config(page_title="Trip Planner", layout="wide")  # Must be first

import json
import os
from datetime import date
import pandas as pd
import plotly.express as px
import requests
from trip_utils import apply_fancy_theme, export_to_excel, export_to_csv

# -----------------------------
# Apply theme
# -----------------------------
apply_fancy_theme()

# -----------------------------
# Constants
# -----------------------------
DATA_FILE = "trip_data.json"
GROQ_API_KEY = st.secrets.get("GROQ", {}).get("API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"  # Correct endpoint

# -----------------------------
# Helpers
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def local_delete_expense(trip_index, expense_index):
    trips = load_data()
    if 0 <= trip_index < len(trips):
        expenses = trips[trip_index].get("expenses", [])
        if 0 <= expense_index < len(expenses):
            removed = expenses.pop(expense_index)
            trips[trip_index]["expenses"] = expenses
            save_data(trips)
            return removed
    return None

# -----------------------------
# Session state
# -----------------------------
if "refresh" not in st.session_state:
    st.session_state.refresh = False

# -----------------------------
# App UI
# -----------------------------
st.title("🌍 Trip Planner by itsolutions.mm (0949567820)")

# --- Sidebar: Add New Trip ---
st.sidebar.header("Add New Trip")
with st.sidebar.form("new_trip"):
    destination = st.text_input("Destination")
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())
    budget = st.number_input("Budget (THB)", min_value=0.0, value=12000.0, step=500.0)
    submit_trip = st.form_submit_button("Save Trip")

    if submit_trip and destination:
        trip_data = {
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "expenses": [],
            "budget": budget
        }
        trips_local = load_data()
        trips_local.append(trip_data)
        save_data(trips_local)
        st.sidebar.success("Trip saved locally.")
        st.session_state.refresh = not st.session_state.refresh

# --- Load trips ---
trips = load_data()
if trips:
    trip_index = st.selectbox(
        "Select a Trip",
        range(len(trips)),
        format_func=lambda i: f"{i}. {trips[i]['destination']}"
    )
    selected_trip = trips[trip_index]
    st.subheader(f"✈️ {selected_trip['destination']} ({selected_trip['start_date']} → {selected_trip['end_date']})")

    # --- Trip Budget ---
    current_budget = selected_trip.get("budget", 12000.0)
    new_budget = st.number_input("Set Budget (THB)", value=current_budget, step=500.0, key="budget_input")
    if new_budget != current_budget:
        trips[trip_index]["budget"] = new_budget
        save_data(trips)
        selected_trip["budget"] = new_budget
        st.success(f"Budget updated to {new_budget:,.0f} THB")

    # --- Add Expense ---
    with st.form("add_expense"):
        date_input_exp = st.date_input("Expense Date", value=date.today())
        category = st.selectbox("Category", ["Food","Transport","Attractions","Accommodation","Shopping","Other"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        currency = st.selectbox("Currency", ["THB (฿)","USD ($)"], index=0)
        description = st.text_input("Description", "")
        submit_expense = st.form_submit_button("Add Expense")
        if submit_expense:
            expense = {
                "date": str(date_input_exp),
                "category": category,
                "amount": amount,
                "currency": currency,
                "description": description
            }
            trips[trip_index].setdefault("expenses", []).append(expense)
            save_data(trips)
            st.success("Expense added!")
            st.session_state.refresh = not st.session_state.refresh

    # --- Expenses Table & Delete ---
    expenses = selected_trip.get("expenses", [])
    if expenses:
        st.write("💰 Expenses")
        for i, e in enumerate(expenses):
            col1, col2 = st.columns([8,1])
            with col1:
                st.write(f"{i+1}. {e.get('date','')} | {e.get('category','')} | "
                          f"{e.get('amount',0.0)} {e.get('currency','THB (฿)')} | {e.get('description','')}")
            with col2:
                if st.button(f"Delete {i+1}", key=f"del_{i}"):
                    local_delete_expense(trip_index, i)
                    st.success(f"Expense {i+1} deleted")
                    st.session_state.refresh = not st.session_state.refresh

        # --- Total Expenses by Currency ---
        totals = {}
        for e in expenses:
            curr = e.get("currency","THB (฿)")
            totals[curr] = totals.get(curr, 0) + e.get("amount",0.0)
        for curr, amt in totals.items():
            st.write(f"**Total Spent ({curr}):** {amt:.2f}")

        # --- Visual Charts ---
        df_exp = pd.DataFrame(expenses)
        for col in ["category","amount","currency"]:
            if col not in df_exp.columns:
                df_exp[col] = "Unknown" if col!="amount" else 0.0
        fig_cat = px.bar(
            df_exp.groupby("category", as_index=False)["amount"].sum(),
            x="category", y="amount", color="category", title="Total Expenses by Category"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

        fig_curr = px.pie(
            df_exp.groupby("currency", as_index=False)["amount"].sum(),
            names="currency", values="amount", title="Expenses by Currency"
        )
        fig_curr.update_traces(textinfo='label+percent', hoverinfo='label+value+percent')
        st.plotly_chart(fig_curr, use_container_width=True)

        # --- Export to Excel ---
        if st.button("💾 Export Expenses to Excel"):
            df_export = pd.DataFrame(expenses)
            if not df_export.empty:
                import io
                excel_buffer = io.BytesIO()
                df_export.to_excel(excel_buffer, index=False, engine='openpyxl')
                st.download_button(
                    label="Download Excel",
                    data=excel_buffer,
                    file_name=f"{selected_trip['destination']}_expenses.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# --- AI Itinerary using Groq ---
extra_prompt = st.text_area(
    "Add extra instructions (optional) for AI",
    placeholder="E.g., vegetarian restaurants, budget under 1500 THB, adventure activities..."
)

if st.button("🧠 Generate AI Itinerary"):
    if not GROQ_API_KEY:
        st.warning("Groq API key not found! AI itinerary cannot be generated. Please add it in Streamlit Secrets.")
    else:
        messages = [
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": f"Plan a trip to {selected_trip['destination']} from {selected_trip['start_date']} to {selected_trip['end_date']}, considering these expenses: {selected_trip.get('expenses',[])}."},
        ]
        if extra_prompt:
            messages.append({"role": "user", "content": extra_prompt})

        payload = {
            "model": "llama-3.3-70b-versatile",  # Replace with your available model
            "messages": messages,
            "max_tokens": 500,
        }

        try:
            response = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                answer = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No answer returned.")
                st.markdown(answer)
            else:
                st.error(f"Groq API request failed. Status: {response.status_code}, {response.text}")
        except Exception as e:
            st.error(f"AI request failed: {e}")

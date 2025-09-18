import streamlit as st
import requests
import json
import os

FASTAPI_URL = "http://127.0.0.1:8000"

DATA_FILE = "trip_data.json"

# Utility to load local trips (from FastAPI’s JSON)
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# UI
st.set_page_config(page_title="Trip Planner", layout="centered")

st.title("🌍 Trip Planner with Expenses + AI")

# Sidebar: Add trip
st.sidebar.header("Add New Trip")
with st.sidebar.form("new_trip"):
    destination = st.text_input("Destination")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    submit_trip = st.form_submit_button("Save Trip")

    if submit_trip and destination:
        trip_data = {
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "expenses": [],
        }
        # Save via FastAPI
        res = requests.post(f"{FASTAPI_URL}/trip_data", json=trip_data)
        st.sidebar.success("Trip added!")

# Select trip
trips = load_data()
trip_names = [f"{i}. {t['destination']}" for i, t in enumerate(trips)]
trip_index = st.selectbox("Select a Trip", range(len(trips)), format_func=lambda i: trip_names[i] if trips else "No trips")

if trips:
    selected_trip = trips[trip_index]
    st.subheader(f"✈️ {selected_trip['destination']} ({selected_trip['start_date']} → {selected_trip['end_date']})")

       # Add expense
    with st.form("add_expense"):
        date = st.date_input("Expense Date")
        category = st.selectbox("Category", ["Food", "Transport", "Attractions", "Accommodation", "Other"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        
        # 🔥 Currency selector
        currency = st.selectbox("Currency", ["THB (฿)", "USD ($)"], index=0)
        
        description = st.text_input("Description", "")
        submit_expense = st.form_submit_button("Add Expense")

        if submit_expense:
            expense = {
                "date": str(date),
                "category": category,
                "amount": amount,
                "currency": currency,   # save currency
                "description": description,
            }
            res = requests.post(f"{FASTAPI_URL}/trip_data/{trip_index}/expense", json=expense)
            st.success("Expense added!")

    # Show expenses
    st.write("💰 Expenses")
    if selected_trip["expenses"]:
        # Display full expense table with currency
        st.table(selected_trip["expenses"])

        # Compute total grouped by currency
        totals = {}
        for e in selected_trip["expenses"]:
            curr = e.get("currency", "USD ($)")  # fallback
            totals[curr] = totals.get(curr, 0) + e["amount"]

        # Show totals
        for curr, amt in totals.items():
            st.write(f"**Total Spent ({curr}):** {amt:.2f}")
    else:
        st.info("No expenses yet.")
    
    # Show expenses with delete buttons
        st.write("💰 Expenses")
        if selected_trip["expenses"]:
           for i, e in enumerate(selected_trip["expenses"]):
               date = e.get("date", "")
               category = e.get("category", "")
               amount = e.get("amount", 0.0)
               currency = e.get("currency", "USD ($)")  # fallback if missing
               description = e.get("description", "")
        
               # Show each expense as text + delete button
               col1, col2 = st.columns([8, 1])
               with col1:
                  st.write(f"{i+1}. {date} | {category} | {amount} {currency} | {description}")
               with col2:
                   if st.button(f"Delete Expense {i+1}", key=f"del_{i}"):
                      res = requests.delete(f"{FASTAPI_URL}/trip_data/{trip_index}/expense/{i}")
                      if res.ok:
                          st.success(f"Deleted expense {i+1}")
                          st.experimental_rerun()  # refresh UI
                   else:
                       st.error("Failed to delete expense")
        else:
            st.info("No expenses yet.")
    

    # AI Itinerary
    if st.button("🧠 Generate AI Itinerary"):
        question = f"Plan a trip to {selected_trip['destination']} from {selected_trip['start_date']} to {selected_trip['end_date']}, considering these expenses: {selected_trip['expenses']}. Suggest activities within budget."
        res = requests.post(f"{FASTAPI_URL}/ask_ai", json={"question": question})
        if res.ok:
            st.markdown(res.json()["answer"])
        else:
            st.error("AI request failed.")
import streamlit as st
st.set_page_config(page_title="Trip Planner", layout="wide")  # MUST be first Streamlit command

import requests
import json
import os
from datetime import date
import pandas as pd
import plotly.express as px
from trip_utils import apply_fancy_theme, export_to_excel, export_to_csv

# Apply custom theme AFTER page config
apply_fancy_theme()

# Constants
FASTAPI_URL = "http://127.0.0.1:8000"
DATA_FILE = "trip_data.json"

# -------------------------
# Helpers: load / save local
# -------------------------
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

# -------------------------
# Local delete helpers
# -------------------------
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

# -------------------------
# Streamlit session state refresh
# -------------------------
if "refresh" not in st.session_state:
    st.session_state.refresh = False

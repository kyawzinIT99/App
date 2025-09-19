# -------------------------
# trip_utils.py (Bright Theme for Family Use)
# -------------------------
import streamlit as st
import pandas as pd
import io

# -------------------------
# Streamlit Custom Styles
# -------------------------
def apply_fancy_theme(bg_color="#B8F2E6", text_color="#0B3C5D", accent_color="#F4D35E"):
    """
    Apply a bright and family-friendly custom theme to the Streamlit app.
    """
    st.markdown(
        f"""
        <style>
        /* App background and main text */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {accent_color};
            font-weight: bold;
        }}
        /* Buttons */
        div.stButton > button {{
            background-color: {accent_color};
            color: {text_color};
            font-weight: bold;
            border-radius: 12px;
            padding: 0.6em 1.2em;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        }}
        div.stButton > button:hover {{
            background-color: #F3C623;
            color: #0B3C5D;
        }}
        /* Sidebar */
        .css-1d391kg, .css-1d391kg * {{
            background-color: #0B3C5D !important;
            color: #F4D35E !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# Export Functions
# -------------------------
def export_to_excel(df, filename="export.xlsx"):
    """
    Return a Streamlit download button for Excel file.
    """
    try:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        st.download_button(
            label="💾 Download Excel",
            data=excel_buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ModuleNotFoundError:
        st.error("openpyxl module not installed. Run `pip install openpyxl`")

def export_to_csv(df, filename="export.csv"):
    """
    Return a Streamlit download button for CSV file.
    """
    csv_buffer = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download CSV",
        data=csv_buffer,
        file_name=filename,
        mime="text/csv"
    )

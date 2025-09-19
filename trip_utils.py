# trip_utils.py
import streamlit as st
import pandas as pd
import io

# -------------------------
# Streamlit Custom Styles
# -------------------------
def apply_fancy_theme(bg_color="#AAC4B5", text_color="#302B2B", accent_color="#B8C0B2"):
    """
    Apply a custom background and accent colors to the Streamlit app.
    """
    st.markdown(
        f"""
        <style>
        /* Background and main text color */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            color: {accent_color};
        }}
        /* Buttons */
        div.stButton > button {{
            background-color: {accent_color};
            color: {text_color};
            border-radius: 12px;
            padding: 0.5em 1em;
        }}
        /* Sidebar */
        .css-1d391kg {{
            background-color: #2c2c3e;
            color: {text_color};
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

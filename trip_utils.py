# trip_utils.py
import streamlit as st
import pandas as pd
import io

# -------------------------
# Streamlit Custom Styles
# -------------------------
def apply_fancy_theme(bg_color="#ffffff", text_color="#1f2937", accent_color="#0d47a1", title_color="#ff5722"):
    """
    Apply a custom background and accent colors to the Streamlit app.
    - bg_color: main app background
    - text_color: main text
    - accent_color: headings and buttons
    - title_color: main app title
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
            font-weight: 700;
        }}
        /* Main App Title */
        .main-title {{
            color: {title_color};
            font-size: 48px;
            font-weight: 900;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        /* Buttons */
        div.stButton > button {{
            background-color: {accent_color};
            color: #ffffff;  /* white text on buttons for contrast */
            border-radius: 12px;
            padding: 0.5em 1em;
            font-weight: 600;
        }}
        /* Sidebar */
        .css-1d391kg {{
            background-color: #e0f2ff;  /* light blue sidebar */
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
    csv_buffer = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download CSV",
        data=csv_buffer,
        file_name=filename,
        mime="text/csv"
    )

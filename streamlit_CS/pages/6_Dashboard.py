import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Setup
st.set_page_config(page_title="Dashboard")

# Read csv
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "PandemicChronoTable.csv")
df = pd.read_csv(data_path)

# --- Custom Styles ---
st.markdown("""
    <style>
        .top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: #0E1117;
            padding: 0.75rem 1.5rem;
            border-bottom: 1px solid #30333A;
        }
        .top-bar-left, .top-bar-center, .top-bar-right {
            display: flex;
            align-items: center;
        }
        .top-bar-center {
            flex: 1;
            justify-content: center;
            color: white;
            font-size: 1.25rem;
            font-weight: 600;
        }
        button[title="View fullscreen"] {visibility: hidden;}  /* Hides Streamlit default fullscreen button */
    </style>
""", unsafe_allow_html=True)

# --- Top Bar Layout ---
with st.container():
    st.markdown(
        """
        <div class="top-bar">
            <div class="top-bar-left">
                <button onclick="window.parent.postMessage({type: 'sidebar-toggle'}, '*')">☰</button>
            </div>
            <div class="top-bar-center">
                Home
            </div>
            <div class="top-bar-right"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Sidebar ---
with st.sidebar:
    st.header("Navigation")
    st.write("Choose a section:")
    st.button("Dashboard Home")
    st.button("Statistics")
    st.button("Trends")

# --- Main Content ---
st.title("Pandemics Through History")
st.dataframe(df.head())
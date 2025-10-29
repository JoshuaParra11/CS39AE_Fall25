import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Setup
st.set_page_config(page_title="Dashboard")

# Read csv
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "PandemicChronoTable.csv")
df = pd.read_csv(data_path)

# --- Initialize Session State ---
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- CSS for Top Bar ---
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
        .sidebar-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Toggle Logic ---
def toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open


# --- Top Bar ---
col1, col2, col3 = st.columns([1, 5, 1])
with col1:
    st.button("☰", on_click=toggle_sidebar, key="sidebar_btn")
with col2:
    st.markdown(f"<div style='text-align:center; font-size:1.25rem; font-weight:600;'>{st.session_state.page}</div>", unsafe_allow_html=True)
with col3:
    st.write("")  # Placeholder for future icons


# --- Sidebar ---
if st.session_state.sidebar_open:
    with st.sidebar:
        st.header("Navigation")
        selected = st.selectbox(
            "Go to",
            ["Home", "Data", "About Me"],
            index=["Home", "Data", "About Me"].index(st.session_state.page),
        )
        st.session_state.page = selected

# --- Dynamic Page Content ---
def render_home():
    st.title("Pandemics Through History")
    st.write("Welcome to the Pandemic Dashboard. Explore data and insights about pandemics through history.")

def render_data():
    st.title("Data Overview")
    st.dataframe(df.head())

def render_about():
    st.title("About Me")
    st.write("This dashboard was created to visualize pandemics data using Streamlit and Python.")

page_renderer = {
    "Home": render_home,
    "Data": render_data,
    "About Me": render_about,
}

# --- Render the Selected Page ---
page_renderer[st.session_state.page]()
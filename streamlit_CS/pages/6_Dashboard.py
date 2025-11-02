import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Setup ---
st.set_page_config(page_title="Dashboard", layout="wide")

# --- Load Data ---
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "PandemicChronoTable.csv")
df = pd.read_csv(data_path)

# --- Session State ---
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- CSS ---
st.markdown("""
<style>
/* --- Top Bar --- */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #0E1117;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid #333;  /* same line weight and color as sidebar button dividers */
    position: relative;
    z-index: 100;
}
.top-bar-center {
    flex: 1;
    justify-content: center;
    color: white;
    font-size: 1.25rem;
    font-weight: 600;
    text-align: center;
}

/* --- Sidebar --- */
div[data-testid="stHorizontalBlock"] > div:first-child {
    border-right: 2px solid #30333A; /* divider between sidebar and main area */
    background-color: #0E1117; /* subtle darker background for sidebar area */
}

/* --- Sidebar Buttons --- */
.stButton > button {
    border: none;
    border-bottom: 1px solid #333; /* horizontal dividers between buttons */
    background-color: transparent;
    color: white;
    text-align: left;
    font-size: 1rem;
    padding: 0.6rem 0.8rem;
}
.stButton > button:hover {
    background-color: #1A1D23;
}

/* --- Toggle Button --- */
.sidebar-toggle {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    margin: 0;
}

/* --- Misc --- */
button[title="View fullscreen"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- Toggle Sidebar ---
def toggle_sidebar():
    st.session_state.sidebar_open = not st.session_state.sidebar_open


# --- Top Bar ---
with st.container():
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        icon = "←" if st.session_state.sidebar_open else "☰"
        st.button(icon, on_click=toggle_sidebar, key="sidebar_btn")
    with col2:
        st.markdown(f"<div class='top-bar-center'>{st.session_state.page}</div>", unsafe_allow_html=True)
    with col3:
        st.write("")


# --- Layout with Custom Sidebar ---
if st.session_state.sidebar_open:
    sidebar_col, main_col = st.columns([1.2, 4])
else:
    sidebar_col, main_col = st.columns([0.05, 4.95])

with sidebar_col:
    if st.session_state.sidebar_open:
        st.markdown("<br>", unsafe_allow_html=True)  # small space below toggle

        if st.button("Home", use_container_width=True):
            st.session_state.page = "Home"
            st.session_state.sidebar_open = False
            st.rerun()

        if st.button("Data", use_container_width=True):
            st.session_state.page = "Data"
            st.session_state.sidebar_open = False
            st.rerun()

        if st.button("About Me", use_container_width=True):
            st.session_state.page = "About Me"
            st.session_state.sidebar_open = False
            st.rerun()
    else:
        st.write("")  # keeps layout consistent


# --- Template Slider State ---
if "data_template" not in st.session_state:
    st.session_state.data_template = 0  # start at Template 0 (the map view)

# --- Page Renderers ---
def render_home():
    st.title("Pandemics Through History")
    st.write("Welcome to the Pandemic Dashboard. Explore data and insights about pandemics through history.")

def render_data():
    st.title("Data Overview")

    # --- Horizontal Navigation Bar for Templates ---
col_prev, col_label, col_next = st.columns([0.5, 5, 0.5])

arrow_style = """
    <style>
    .nav-btn button {
        background: none;
        border: 1px solid #444;
        color: white;
        font-size: 1.25rem;
        cursor: pointer;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
    }
    .nav-btn button:hover {
        background-color: #1A1D23;
    }
    </style>
"""
st.markdown(arrow_style, unsafe_allow_html=True)

with col_prev:
    with st.container():
        st.markdown("<div class='nav-btn'>", unsafe_allow_html=True)
        if st.button("←", key="prev_template"):
            st.session_state.data_template = (st.session_state.data_template - 1) % 3
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

with col_label:
    templates = ["Template 1: Map View", "Template 2: Statistics", "Template 3: Insights"]
    st.markdown(f"<h5 style='text-align:center; margin-top:0.3rem'>{templates[st.session_state.data_template]}</h5>", unsafe_allow_html=True)

with col_next:
    with st.container():
        st.markdown("<div class='nav-btn'>", unsafe_allow_html=True)
        if st.button("→", key="next_template"):
            st.session_state.data_template = (st.session_state.data_template + 1) % 3
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Template Content ---
    if st.session_state.data_template == 0:
        st.subheader("🌍 Template 1: Interactive Map")
        st.write("Here we'll show the Folium heatmap and related visuals.")
        # (later: embed folium map + stats)
    elif st.session_state.data_template == 1:
        st.subheader("📊 Template 2: Statistical Overview")
        st.write("Placeholder for data summaries and KPIs.")
    elif st.session_state.data_template == 2:
        st.subheader("🧠 Template 3: Insights")
        st.write("Placeholder for insights text or markdown summaries.")

def render_about():
    st.title("About Me")
    st.write("This dashboard was created to visualize pandemics data using Streamlit and Python.")


page_renderer = {
    "Home": render_home,
    "Data": render_data,
    "About Me": render_about,
}

# --- Render Selected Page ---
with main_col:
    page_renderer[st.session_state.page]()
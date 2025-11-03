import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import geopandas as gpd
import folium
import plotly.express as px
import os

# --- Page Setup ---
st.set_page_config(page_title="Dashboard", layout="wide")

# --- Load Data ---
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "PandemicChronoTable.csv")
df = pd.read_csv(data_path)

# Normalize continent names for consistent matching
df["Continent"] = df["Continent"].str.strip().str.title()

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

    # --- Layout ---
    map_col, details_col = st.columns([2, 1])

    # --- Data Prep ---
    geojson_path = os.path.join(os.path.dirname(__file__), "..", "data", "continents.geojson")
    map_df = df.dropna(subset=["Latitude", "Longitude", "Continent"])
    
    continent_list = ["Select a Continent..."] + sorted(map_df["Continent"].unique().tolist())

    # --- Right Column: Details & Controls ---
    with details_col:
        st.subheader("Filters")
        
        selected_continent = st.selectbox(
            "First, choose a continent:",
            options=continent_list,
            key="continent_selector"
        )

        selected_pandemic_name = None
        
        if selected_continent and selected_continent != "Select a Continent...":
            pandemic_list = ["Select a Pandemic..."] + sorted(
                map_df[map_df["Continent"] == selected_continent]["Disease"].unique().tolist()
            )
            
            selected_pandemic_name = st.selectbox(
                f"Next, choose a pandemic in {selected_continent}:",
                options=pandemic_list,
                key="pandemic_selector"
            )

    # --- Left Column: Map ---
    with map_col:
        st.subheader("≡ƒù║∩╕Å Pandemic Map")

        # --- Set Map's Initial View ---
        map_center = [20, 0]
        zoom_level = 2
        
        # If a pandemic is selected, find its data to center the map
        if selected_pandemic_name and selected_pandemic_name != "Select a Pandemic...":
            pandemic_rows = map_df[map_df["Disease"] == selected_pandemic_name]
            if not pandemic_rows.empty:
                # Center on the average location for that pandemic
                map_center = [pandemic_rows["Latitude"].mean(), pandemic_rows["Longitude"].mean()]
                zoom_level = 4

        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            control_scale=True
        )

        # --- Add Continent Layer with Hover Tooltip (Always Visible) ---
        folium.GeoJson(
            geojson_path,
            name="continents",
            style_function=lambda feature: {
                "fillColor": "#1DB954",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.1,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["CONTINENT"], 
                aliases=[""],
                style=("background-color: #333; color: white; font-family: sans-serif; font-size: 12px; padding: 5px;")
            )
        ).add_to(m)

        # --- If a Pandemic is Selected, Add a HeatMap ---
        if selected_pandemic_name and selected_pandemic_name != "Select a Pandemic...":
            from folium.plugins import HeatMap
            
            pandemic_rows = map_df[map_df["Disease"] == selected_pandemic_name]
            
            if not pandemic_rows.empty:
                # Create a list of [lat, lon] for the heatmap
                heat_data = pandemic_rows[["Latitude", "Longitude"]].values.tolist()
                
                # Add the heatmap layer to the map
                HeatMap(heat_data, radius=25, blur=15).add_to(m)
            else:
                st.warning(f"No location data found for {selected_pandemic_name}")

        # --- Render the Final Map in Streamlit ---
        st_folium(m, key="main_map", width=800, height=500)

    # --- Insights Section ---
    st.markdown("---")
    st.subheader("Insights")
    st.write(
        """
        This section is for your text analysis. For example, you could note that early pandemics 
        are often localized to specific empires (e.g., Roman, Byzantine), while later events 
        show more global spread due to increased trade and travel. The map interaction helps 
        visualize this geographic distribution over time.
        """
    )

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
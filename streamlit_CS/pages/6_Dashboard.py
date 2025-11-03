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
    
    required_cols_for_dropna = ["Latitude", "Longitude", "Continent", "Date", "Disease", "Death toll (estimate)"]

    map_df = df[(df["Latitude"] != 0) & (df["Longitude"] != 0)].dropna(
        subset=required_cols_for_dropna
    )
    
    disease_list = ["Select a Pandemic..."] + sorted(map_df["Disease"].unique().tolist())

    # --- Right Column: Details & Controls ---
    with details_col:
        st.subheader("Filters")
        
        selected_disease = st.selectbox(
            "Choose a pandemic to display:",
            options=disease_list,
            key="disease_selector"
        )

    # --- Left Column: Map ---
    with map_col:
        st.subheader("Pandemic Map")

        map_center = [20, 0]
        zoom_level = 2
        
        if selected_disease and selected_disease != "Select a Pandemic...":
            pandemic_rows = map_df[map_df["Disease"] == selected_disease]
            if not pandemic_rows.empty:
                map_center = [pandemic_rows["Latitude"].mean(), pandemic_rows["Longitude"].mean()]
                zoom_level = 3

        m = folium.Map(
            location=map_center,
            zoom_start=zoom_level,
            control_scale=True
        )

        folium.GeoJson(
            geojson_path,
            name="continents",
            style_function=lambda feature: {"fillColor": "#1DB954", "color": "black", "weight": 1, "fillOpacity": 0.1},
            tooltip=folium.GeoJsonTooltip(
                fields=["CONTINENT"], 
                aliases=[""],
                style=("background-color: #333; color: white; font-family: sans-serif; font-size: 12px; padding: 5px;")
            )
        ).add_to(m)

        if selected_disease and selected_disease != "Select a Pandemic...":
            from folium.plugins import HeatMap
            
            pandemic_rows = map_df[map_df["Disease"] == selected_disease]
            
            if not pandemic_rows.empty:
                heat_data = pandemic_rows[["Latitude", "Longitude"]].values.tolist()
                HeatMap(heat_data, radius=25, blur=15).add_to(m)

                for _, row in pandemic_rows.iterrows():
                    popup_html = f"""
                    <div style="min-width: 200px;">
                        <b>Location:</b> {row['Location']}<br>
                        <b>Time:</b> {row['Date']}<br>
                        <b>Deaths:</b> {row['Death toll (estimate)']}
                    </div>
                    """
                    folium.Marker(
                        location=[row["Latitude"], row["Longitude"]],
                        popup=popup_html,
                        tooltip=row['Location'],
                        icon=folium.Icon(color="red", icon="info-sign"),
                    ).add_to(m)
            else:
                st.warning(f"No location data found for {selected_disease}")

        st_folium(m, key="main_map", width=800, height=500)

    # --- Insights Section ---
    st.markdown("---")
    st.subheader("Insights")
    
    if selected_disease and selected_disease != "Select a Pandemic...":
        st.markdown(f"**{selected_disease}** affected:")
        pandemic_rows = map_df[map_df["Disease"] == selected_disease]
        for _, row in pandemic_rows.iterrows():
            st.markdown(
                f"- **Location:** {row['Location']}<br>"
                f"  **Time:** {row['Date']}<br>"
                f"  **Deaths:** {row['Death toll (estimate)']}"
            )
    else:
        st.write(
            """
            Select a pandemic from the dropdown to see its geographic spread. The heatmap shows the
            density of recorded occurrences, while the red markers pinpoint specific locations with
            available data.
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
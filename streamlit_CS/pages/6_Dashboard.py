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

    # --- Load Data ---
    geojson_path = os.path.join(os.path.dirname(__file__), "..", "data", "continents.geojson")
    map_df = df.dropna(subset=["Latitude", "Longitude", "Continent"])

    # --- Initialize Session State ---
    if "selected_continent" not in st.session_state:
        st.session_state.selected_continent = None
    if "selected_pandemic" not in st.session_state:
        st.session_state.selected_pandemic = None

    st.subheader("🗺️ Interactive Map")

    # --- BASE MAP ---
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        no_wrap=True,
        max_bounds=True,
        world_copy_jump=False,
        control_scale=True,
    )

    # --- BACK TO WORLD VIEW BUTTON ---
    if st.session_state.selected_continent or st.session_state.selected_pandemic:
        folium.map.Marker(
            [60, -160],
            icon=folium.DivIcon(
                html="""
                <div style="background-color:white; border:1px solid #999; border-radius:5px;
                            padding:3px 6px; cursor:pointer; font-weight:bold; font-size:12px;">
                    ⬅ Back
                </div>"""
            ),
            tooltip="Return to world view",
        ).add_to(m)

    # --- 1️⃣ WORLD VIEW: Click continent to zoom ---
    if not st.session_state.selected_continent and not st.session_state.selected_pandemic:
        def on_click(feature):
            return {
                "fillColor": "#1DB954",
                "color": "black",
                "weight": 1.5,
                "fillOpacity": 0.5,
            }

        folium.GeoJson(
            geojson_path,
            name="continents",
            style_function=lambda feature: {
                "fillColor": "#1DB954",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.2,
            },
            highlight_function=on_click,
            tooltip=folium.GeoJsonTooltip(fields=["CONTINENT"], aliases=["Continent:"]),
        ).add_to(m)

        map_output = st_folium(m, key="world_map", width=800, height=500)

        if map_output and map_output.get("last_object_clicked_tooltip"):
            clicked_continent = (
                map_output["last_object_clicked_tooltip"]
                .replace("Continent: ", "")
                .strip()
                .title()
            )
            st.session_state.selected_continent = clicked_continent
            st.rerun()

    # --- 2️⃣ CONTINENT VIEW: Show pandemics in continent ---
    elif st.session_state.selected_continent and not st.session_state.selected_pandemic:
        continent = st.session_state.selected_continent
        continent_pandemics = map_df[map_df["Continent"].str.lower() == continent.lower()]

        if continent_pandemics.empty:
            st.warning(f"No pandemic data found for {continent} in CSV.")
            st.session_state.selected_continent = None
            st.rerun()

        # Fit map to continent bounds
        lats = continent_pandemics["Latitude"].astype(float)
        longs = continent_pandemics["Longitude"].astype(float)
        if not lats.empty and not longs.empty:
            m.fit_bounds([[lats.min(), longs.min()], [lats.max(), longs.max()]])

        # Add pandemic markers
        for _, row in continent_pandemics.iterrows():
            popup_html = f"""
            <div style='font-size:13px'>
                <b>{row['Disease']}</b> ({row['Year']})<br>
                Deaths: {row['Death toll (estimate)']}<br>
                <a href='#' onclick="window.parent.postMessage(
                    {{'type': 'pandemic_select', 'pandemic': '{row['Disease']}' }}, '*')">
                    🔍 View Heatmap
                </a>
            </div>
            """
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=popup_html,
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(m)

        folium.GeoJson(
            geojson_path,
            style_function=lambda feature: {
                "fillColor": "#1DB954" if feature["properties"]["CONTINENT"].lower() == continent.lower() else "#ccc",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.3,
            },
        ).add_to(m)

        st.markdown(f"### 🌍 Pandemics in {continent}")
        st.markdown("Click markers on the map to view details and heatmaps.")

        map_output = st_folium(m, key="continent_map", width=800, height=500)

        # handle back click (check top-left area marker)
        if map_output and map_output.get("last_object_clicked"):
            clicked_lat, clicked_lng = map_output["last_object_clicked"]
            if clicked_lat > 50 and clicked_lng < -100:  # near back button
                st.session_state.selected_continent = None
                st.rerun()

    # --- 3️⃣ PANDEMIC VIEW: Show Heatmap for selected pandemic ---
    elif st.session_state.selected_pandemic:
        pandemic_name = st.session_state.selected_pandemic
        pandemic_rows = map_df[map_df["Disease"].str.lower() == pandemic_name.lower()]

        if pandemic_rows.empty:
            st.warning(f"No coordinate data found for {pandemic_name}")
            st.session_state.selected_pandemic = None
            st.rerun()

        heat_data = pandemic_rows[["Latitude", "Longitude"]].values.tolist()

        from folium.plugins import HeatMap
        HeatMap(heat_data, radius=25, blur=15, min_opacity=0.4).add_to(m)

        m.fit_bounds([[pandemic_rows["Latitude"].min(), pandemic_rows["Longitude"].min()],
                      [pandemic_rows["Latitude"].max(), pandemic_rows["Longitude"].max()]])

        st.markdown(f"### 🔥 {pandemic_name} — Spread Heatmap")
        st.markdown("Use ⬅ Back on the map to return to world view.")

        map_output = st_folium(m, key="heatmap_map", width=800, height=500)

        # Back button area
        if map_output and map_output.get("last_object_clicked"):
            clicked_lat, clicked_lng = map_output["last_object_clicked"]
            if clicked_lat > 50 and clicked_lng < -100:  # near back button
                st.session_state.selected_pandemic = None
                st.session_state.selected_continent = None
                st.rerun()

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
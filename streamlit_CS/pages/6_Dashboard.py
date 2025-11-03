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

    # --- Initialize Session State ---
    if "selected_continent" not in st.session_state:
        st.session_state.selected_continent = None
    if "selected_pandemic" not in st.session_state:
        st.session_state.selected_pandemic = None

    # --- Columns Layout ---
    map_col, details_col = st.columns([2, 1])

    # --- Load GeoJSON ---
    geojson_path = os.path.join(os.path.dirname(__file__), "..", "data", "continents.geojson")
    map_df = df.dropna(subset=["Latitude", "Longitude", "Continent"])

    # --- MAP COLUMN ---
    with map_col:
        st.subheader("Interactive Map")

        # --- If pandemic selected → Show Heatmap ---
        if st.session_state.selected_pandemic:
            pandemic_name = st.session_state.selected_pandemic.split(" (")[0]
            st.write(f"**Showing heatmap for:** {pandemic_name}")

            heat_data = (
                map_df[map_df["Disease"] == pandemic_name][["Latitude", "Longitude"]].values.tolist()
            )

            m = folium.Map(
                location=[20, 0],
                zoom_start=3,
                no_wrap=True,
                max_bounds=True,
                world_copy_jump=False,
                control_scale=True,
            )

            from folium.plugins import HeatMap
            if len(heat_data) > 0:
                HeatMap(heat_data, radius=25, blur=15, min_opacity=0.4).add_to(m)
            else:
                st.warning("No coordinates available for this pandemic.")

            if st.button("← Back to Continent View"):
                st.session_state.selected_pandemic = None
                st.rerun()

            st_folium(m, key="heatmap_view", width=700, height=450)

        # --- Else if continent selected → Show its pandemics list ---
        elif st.session_state.selected_continent:
            continent = st.session_state.selected_continent

            m = folium.Map(
                location=[20, 0],
                zoom_start=2,
                no_wrap=True,
                max_bounds=True,
                world_copy_jump=False,
            )

            # Add GeoJSON with style and zoom animation
            continents_layer = folium.GeoJson(
                geojson_path,
                name="continents",
                style_function=lambda feature: {
                    "fillColor": "#1DB954" if feature["properties"]["CONTINENT"] == continent else "#444",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.3,
                },
            )
            continents_layer.add_to(m)

            # Focus map to the continent area
            try:
                import geopandas as gpd
                gdf = gpd.read_file(geojson_path)
                bounds = gdf[gdf["CONTINENT"] == continent].total_bounds  # [minx, miny, maxx, maxy]
                m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
            except Exception as e:
                st.warning(f"Could not auto-zoom to continent: {e}")

            if st.button("← Back to World View"):
                st.session_state.selected_continent = None
                st.rerun()

            st_folium(m, key="continent_view", width=700, height=450)

        # --- Else: Default world map view ---
        else:
            m = folium.Map(
                location=[20, 0],
                zoom_start=2,
                no_wrap=True,
                max_bounds=True,
                world_copy_jump=False,
            )

            folium.GeoJson(
                geojson_path,
                name="continents",
                style_function=lambda feature: {
                    "fillColor": "#1DB954",
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.2,
                },
                highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.5},
                tooltip=folium.GeoJsonTooltip(fields=["CONTINENT"], aliases=["Continent:"]),
            ).add_to(m)

            map_output = st_folium(m, key="world_map", width=700, height=450)

            if map_output and map_output.get("last_object_clicked_tooltip"):
                clicked_continent = map_output["last_object_clicked_tooltip"]
                st.session_state.selected_continent = clicked_continent
                st.rerun()

    # --- DETAILS COLUMN ---
    with details_col:
        st.subheader("📋 Details & Stats")

        # If a continent is selected but not a pandemic
        if st.session_state.selected_continent and not st.session_state.selected_pandemic:
            continent = st.session_state.selected_continent
            continent_pandemics = map_df[map_df["Continent"] == continent].reset_index()

            if not continent_pandemics.empty:
                pandemic_options = [
                    f"{row['Disease']} ({row['Year']})" for _, row in continent_pandemics.iterrows()
                ]
                selected_option = st.selectbox(
                    "Select a pandemic:",
                    options=pandemic_options,
                    index=None,
                    placeholder="Choose an event..."
                )
                if selected_option:
                    st.session_state.selected_pandemic = selected_option
                    st.rerun()
            else:
                st.info(f"No pandemic data available for {continent}.")
        elif not st.session_state.selected_continent:
            st.info("Click a continent on the map to see pandemics in that region.")
        elif st.session_state.selected_pandemic:
            st.success(f"Currently viewing: {st.session_state.selected_pandemic}")

        st.markdown("---")
        st.markdown("*(Future: summary stats & visuals go here)*")

    # --- INSIGHTS ---
    st.markdown("---")
    st.subheader("Insights")
    st.write(
        """
        This map shows where pandemics have occurred throughout history.
        Click on a continent to explore specific events, and view their spread intensity.
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
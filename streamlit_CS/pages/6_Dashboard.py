import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import HeatMap
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
    # Used to track user selections across reruns
    if "selected_continent" not in st.session_state:
        st.session_state.selected_continent = None
    if "selected_pandemic_index" not in st.session_state:
        st.session_state.selected_pandemic_index = None
    
    # --- Layout ---
    # The map takes 2/3 of the space, details/stats take 1/3
    map_col, details_col = st.columns([2, 1])
    
    # --- Data for the Map ---
    # URL for a GeoJSON file with continent boundaries
    geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/continents.json"
    
    # Filter out data points without coordinates for mapping
    map_df = df.dropna(subset=['Latitude', 'Longitude', 'Continent'])
    
    # --- Back Button Logic ---
    # If a pandemic is selected, show a button to go back to the continent view
    if st.session_state.selected_pandemic_index is not None:
        if st.button("← Back to Continents"):
            st.session_state.selected_continent = None
            st.session_state.selected_pandemic_index = None
            st.rerun()
    
    # --- MAP COLUMN ---
    with map_col:
        st.subheader("🌍 Interactive Map")
    
        # --- Pandemic-Focused View ---
        if st.session_state.selected_pandemic_index is not None:
            pandemic = map_df.loc[st.session_state.selected_pandemic_index]
    
            # Create a map centered on the selected pandemic
            m = folium.Map(
                location=[pandemic['Latitude'], pandemic['Longitude']],
                zoom_start=5
            )
    
            # Add a heatmap layer
            # Note: A heatmap of a single point isn't very visible.
            # For a real "affected zone", you'd need polygon data.
            # Here, we'll just add a prominent marker instead for clarity.
            folium.Marker(
                location=[pandemic['Latitude'], pandemic['Longitude']],
                popup=f"<strong>{pandemic['Disease']}</strong> ({pandemic['Year']})",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
    
            st_folium(m, key="pandemic_map", width=700, height=450)
    
        # --- Continent Selection View ---
        else:
            # Create a map for selecting continents
            m = folium.Map(location=[20, 0], zoom_start=2)
    
            # Add the clickable continent layer
            continents_layer = folium.GeoJson(
                geojson_url,
                name='continents',
                style_function=lambda feature: {
                    'fillColor': '#1DB954',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.2,
                },
                highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.5},
                tooltip=folium.GeoJsonTooltip(fields=['continent'], aliases=['Continent:'])
            ).add_to(m)
    
            # Render the map and capture clicks
            map_output = st_folium(m, key="continent_map", width=700, height=450)
    
            # If a continent is clicked, update the session state
            if map_output and map_output.get("last_object_clicked_tooltip"):
                clicked_continent = map_output["last_object_clicked_tooltip"]
                st.session_state.selected_continent = clicked_continent
                st.rerun()
    
    # --- DETAILS COLUMN ---
    with details_col:
        st.subheader("Details & Stats")
    
        if st.session_state.selected_continent:
            continent = st.session_state.selected_continent
            st.markdown(f"#### Pandemics in **{continent}**")
    
            # Filter pandemics for the selected continent
            continent_pandemics = map_df[map_df['Continent'] == continent].reset_index()
    
            if not continent_pandemics.empty:
                # Create a list of formatted strings for the selectbox
                pandemic_options = [
                    f"{row['Disease']} ({row['Year']})" for index, row in continent_pandemics.iterrows()
                ]
   
                with st.expander("Select a pandemic to view on map", expanded=True):
                    selected_option = st.selectbox(
                        "Choose a pandemic:",
                        options=pandemic_options,
                        index=None, # No default selection
                        placeholder="Select a pandemic..."
                    )
   
                    if selected_option:
                        # Find the index of the selected pandemic to update the map
                        selected_index_in_options = pandemic_options.index(selected_option)
                        original_df_index = continent_pandemics.loc[selected_index_in_options, 'index']
   
                        # Update session state to trigger map change
                        st.session_state.selected_pandemic_index = original_df_index
                        st.rerun()
            else:
                st.info(f"No pandemic data available for {continent}.")
        else:
            st.info("Click a continent on the map to see a list of pandemics.")
   
        # Placeholder for future stats visuals
        st.markdown("---")
        st.markdown("*(Future stats visuals will appear here)*")
   
   
    # --- INSIGHTS SECTION ---
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
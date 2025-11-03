import pandas as pd
import numpy as np
import re
import os

# Load Data
# Correctly construct the path relative to this script file
data_path = os.path.join(os.path.dirname(__file__), "PandemicChronoTable.csv")
df = pd.read_csv(data_path)

# --- DATA CLEANING ---

# Drop useless columns if they exist
df.drop(columns=['Unnamed: 0', 'Ref.'], inplace=True, errors='ignore')

# Separate unknown disease events
df["Disease_Known"] = ~df["Disease"].str.contains("unknown", case=False, na=False)

# --- CONTINENT MAPPING ---
# This mapping helps group locations into continents.
continent_map = {
    # Africa
    "Angola": "Africa", "Angola and Democratic Republic of the Congo": "Africa",
    "Chad": "Africa", "Congo Basin": "Africa", "Darfur, Sudan": "Africa",
    "Democratic Republic of the Congo": "Africa", "Democratic Republic of the Congo and Uganda": "Africa",
    "East Africa": "Africa", "Ethiopia": "Africa", "Ituri Province, Democratic Republic of the Congo": "Africa",
    "Madagascar": "Africa", "Mali": "Africa", "Nigeria": "Africa", "Oju, Nigeria": "Africa",
    "South Africa": "Africa", "Sudan": "Africa", "Uganda": "Africa", "West Africa": "Africa",
    "Western Sahara": "Africa", "Greece, Libya, Egypt, Ethiopia": "Africa",

    # North America
    "Boston, Massachusetts Bay Colony, British North America": "North America", "British North America": "North America",
    "Canada": "North America", "Charleston, British North America": "North America",
    "Charleston and Philadelphia, British North America": "North America", "Flint, Michigan, United States": "North America",
    "Great Plains, United States and Canada": "North America", "Massachusetts Bay Colony": "North America",
    "Massachusetts Bay Colony, British North America": "North America", "Massachusetts Bay Colony, Thirteen Colonies": "North America",
    "Minnesota, United States": "North America", "Mississippi Valley, United States": "North America",
    "Montreal, Canada": "North America", "New France, Canada": "North America", "New Orleans, United States": "North America",
    "New York City, British North America": "North America", "North America": "North America",
    "Pacific Northwest, United States": "North America", "Philadelphia, United States": "North America",
    "Province of Carolina, Thirteen Colonies": "North America", "Southern United States (especially Louisiana and Florida)": "North America",
    "Southern United States (especially New Orleans)": "North America", "Thirteen Colonies": "North America",
    "Thirteen Colonies and New France, Canada": "North America", "United States": "North America",
    "Wyandot people, North America": "North America", "Puerto Rico, Dominican Republic, Mexico": "North America",
    "Southern New England, British North America, especially the Wampanoag people": "North America",

    # South America
    "Americas": "South America", "Argentina": "South America", "Bolivia": "South America", "Brazil": "South America",
    "Buenos Aires, Argentina": "South America", "Cartagena, Colombia": "South America", "Central America": "South America",
    "Chile": "South America", "Colombia": "South America", "Montevideo, Uruguay": "South America",
    "Peru, Chile, Bolivia, Ecuador, Colombia, Mexico, El Salvador, Guatemala": "South America", "South America": "South America",

    # Asia
    "Asia": "Asia", "Bangladesh": "Asia", "Bombay, India": "Asia", "Cambodia": "Asia", "China": "Asia",
    "China, Southeast Asia and Egypt": "Asia", "Hong Kong": "Asia", "India": "Asia", "Indonesia": "Asia",
    "Iran": "Asia", "Iraq": "Asia", "Japan": "Asia", "Kuala Koh, Malaysia": "Asia", "Malaysia": "Asia",
    "Pakistan": "Asia", "Persia": "Asia", "Peshawar, Pakistan": "Asia", "Philippines": "Asia",

    "Singapore": "Asia", "Sri Lanka": "Asia", "Vietnam": "Asia", "Yemen": "Asia", "Middle East": "Asia",
    "Megiddo, land of Canaan": "Asia", "Byzantine Empire, West Asia, Syria, Mesopotamia": "Asia",
    "Bilad al-Sham": "Asia", "Han Dynasty": "Asia",

    # Europe
    "Amsterdam, Netherlands": "Europe", "Augsburg, Germany": "Europe", "Barcelona, Spain": "Europe",
    "British Isles": "Europe", "C├ídiz, Spain": "Europe", "Copenhagen, Denmark": "Europe",
    "Croydon, United Kingdom": "Europe", "Denmark, Sweden, Lithuania": "Europe", "England": "Europe",
    "Europe": "Europe", "France": "Europe", "Iceland": "Europe", "Ireland": "Europe", "Italy": "Europe",
    "Lisbon, Portugal": "Europe", "London, England": "Europe", "London and Westminster, England": "Europe",
    "Malta": "Europe", "Messina, Sicily, Italy": "Europe", "Netherlands": "Europe",
    "Norfolk and Portsmouth, England": "Europe", "Portugal": "Europe", "Prague, Czech Kingdom": "Europe",
    "Romania": "Europe", "Rome, Byzantine Empire": "Europe", "Russia": "Europe", "Spain": "Europe",
    "Staphorst, Netherlands": "Europe", "Tenerife, Spain": "Europe", "United Kingdom": "Europe",
    "Vienna, Austria": "Europe", "Yugoslavia": "Europe", "Roman Empire": "Europe",
    "Britain (England) and later continental Europe": "Europe", "Greece (Northern Greece, Roman Republic)": "Europe",
    "Balkans": "Europe",

    # Oceania
    "Australia": "Oceania", "Fiji": "Oceania", "Fremantle, Western Australia": "Oceania",
    "Hawaiian Kingdom": "Oceania", "New South Wales, Australia": "Oceania", "New Zealand": "Oceania",
    "Papua New Guinea": "Oceania", "Queensland, Australia": "Oceania", "Samoa": "Oceania",
    "Sydney, Australia": "Oceania", "Victoria, Australia": "Oceania",

    # Multiple/Global
    "Asia, Africa, Europe, South America": "Multiple", "Asia, Africa, Europe, and Americas": "Multiple",
    "Asia, Europe": "Multiple", "Asia, Europe, North America": "Multiple", "Asia, North Africa, Europe": "Multiple",
    "Asia-Pacific, Latin America": "Multiple", "Byzantine Empire": "Multiple", "Eurasia and North Africa": "Multiple",
    "Europe and West Asia": "Multiple", "Europe, Asia, Africa": "Multiple", "Europe, North America, South America": "Multiple",
    "Ottoman Empire": "Multiple", "Ottoman Empire, Egypt": "Multiple", "Worldwide": "Global",
    "Worldwide, primarily concentrated in Guinea, Liberia, Sierra Leone": "Global",
    "Byzantine Empire, West Asia, Africa": "Multiple",
}
df["Continent"] = df["Location"].map(continent_map).fillna("Unknown")
df["Continent"] = df["Continent"].str.strip().str.title()


# --- COORDINATE MAPPING (REFINED) ---
# More specific coordinates to fix heatmap centering issues.
coords_map = {
    "Europe": (54.5, 15.2), "Asia": (34.0, 100.6), "Africa": (1.5, 17.3),
    "North America": (40.0, -100.0), "South America": (-15.6, -56.1), "Oceania": (-22.7, 140.0),
    "Worldwide": (0, 0), "Global": (0, 0), "Multiple": (30, 30),
    "Roman Empire": (41.9, 12.5), "China": (35.8, 104.1), "India": (20.5, 78.9),
    "United States": (37.0, -95.7), "Russia": (61.5, 105.3), "England": (52.3, -1.1),
    "Italy": (41.8, 12.5), "France": (46.6, 1.8), "Spain": (40.4, -3.7),
    "Mexico": (23.6, -102.5), "Japan": (36.2, 138.2), "Egypt": (26.8, 30.8),
    "Iran": (32.4, 53.6), "Persia": (32.4, 53.6), "Ottoman Empire": (39.9, 32.8),
    "Byzantine Empire": (41.0, 28.9), "West Africa": (9.6, -2.2),
    "Central America": (12.8, -86.2), "South Africa": (-30.5, 22.9),
    "Australia": (-25.2, 133.7), "Brazil": (-14.2, -51.9), "Canada": (56.1, -106.3),
    "United Kingdom": (55.3, -3.4), "Germany": (51.1, 10.4),
    "Scandinavia": (62.0, 15.0), "Middle East": (29.2, 42.6),
    "Southeast Asia": (4.2, 101.9), "Eurasia and North Africa": (35, 40),
    "Asia, Europe, North America": (45, 10), "Europe, Asia, Africa": (30, 30),
    "Asia, North Africa, Europe": (35, 25), "Asia, Africa, Europe, and Americas": (0,0),
}

# Function to get the best coordinate match
def get_coords(location):
    # First, try for an exact match
    if location in coords_map:
        return coords_map[location]
    # If no exact match, find the best partial match from the keys
    for key, val in coords_map.items():
        if key.lower() in location.lower():
            return val
    return (0, 0) # Default if no match is found

df["Coordinates"] = df["Location"].apply(get_coords)
df[["Latitude", "Longitude"]] = df["Coordinates"].apply(pd.Series)


# --- DEATH TOLL PARSING ---
def parse_death_toll(value):
    if pd.isna(value): return np.nan
    s = str(value).lower().strip()
    if any(tok in s for tok in ("unknown", "n/a", "not known", "no data")): return np.nan

    unit = 1
    if "billion" in s: unit = 1_000_000_000
    elif "million" in s: unit = 1_000_000
    elif "thousand" in s: unit = 1_000

    numbers = re.findall(r"[\d,.]+", s)
    if not numbers: return np.nan
    
    cleaned_numbers = []
    for n in numbers:
        try:
            cleaned_numbers.append(float(n.replace(",", "")))
        except ValueError:
            continue
            
    if not cleaned_numbers: return np.nan
    
    # Return the highest number found, multiplied by the unit
    return max(cleaned_numbers) * unit

df["Death Toll (est)"] = df["Death toll (estimate)"].apply(parse_death_toll)


# --- FINAL CLEANUP & SAVE ---
# Remove rows where essential data is missing for the map
df_cleaned = df.dropna(subset=["Latitude", "Longitude", "Death Toll (est)", "Continent"])
df_cleaned = df_cleaned[df_cleaned["Continent"] != "Unknown"]

# Overwrite the original CSV with the cleaned and processed data
# This ensures the Streamlit app always reads clean data
output_path = os.path.join(os.path.dirname(__file__), "PandemicChronoTable.csv")
df_cleaned.to_csv(output_path, index=False)

print("Data cleaning and processing complete. `PandemicChronoTable.csv` has been updated.")
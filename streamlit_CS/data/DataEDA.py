import pandas as pd
import numpy as np
import re
import os

# Load Data
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "PandemicChronoTable.csv")
df = pd.read_csv(data_path)

print(df.columns)
print(df.head(10))
print(df.info)

# Drop useless columns
df.drop(columns=['Unnamed: 0', 'Ref.'], errors='ignore')

# Separate unknown disease events
df["Disease_Known"] = ~df["Disease"].str.contains("unknown", case=False, na=False)

# Show unique location values (for known diseases only)
known_df = df[df["Disease_Known"]]

unique_locations = known_df["Location"].dropna().unique()
# print(f"\nTotal unique locations (known diseases): {len(unique_locations)}\n")
# print(sorted(unique_locations))

# --- Continent Mapping ---
continent_map = {
    # 🌍 Africa
    "Angola": "Africa",
    "Angola and Democratic Republic of the Congo": "Africa",
    "Byzantine Empire, West Asia, Africa": "Africa",
    "Byzantine Empire, West Asia, Syria, Mesopotamia": "Asia",
    "Chad": "Africa",
    "Congo Basin": "Africa",
    "Darfur, Sudan": "Africa",
    "Democratic Republic of the Congo": "Africa",
    "Democratic Republic of the Congo and Uganda": "Africa",
    "East Africa": "Africa",
    "Ethiopia": "Africa",
    "Ituri Province, Democratic Republic of the Congo": "Africa",
    "Madagascar": "Africa",
    "Mali": "Africa",
    "Nigeria": "Africa",
    "Oju, Nigeria": "Africa",
    "South Africa": "Africa",
    "Sudan": "Africa",
    "Uganda": "Africa",
    "West Africa": "Africa",
    "Western Sahara": "Africa",

    # 🌎 North America
    "Boston, Massachusetts Bay Colony, British North America": "North America",
    "British North America": "North America",
    "Canada": "North America",
    "Charleston, British North America": "North America",
    "Charleston and Philadelphia, British North America": "North America",
    "Flint, Michigan, United States": "North America",
    "Great Plains, United States and Canada": "North America",
    "Massachusetts Bay Colony": "North America",
    "Massachusetts Bay Colony, British North America": "North America",
    "Massachusetts Bay Colony, Thirteen Colonies": "North America",
    "Minnesota, United States": "North America",
    "Mississippi Valley, United States": "North America",
    "Montreal, Canada": "North America",
    "New France, Canada": "North America",
    "New Orleans, United States": "North America",
    "New York City, British North America": "North America",
    "North America": "North America",
    "Pacific Northwest, United States": "North America",
    "Philadelphia, United States": "North America",
    "Province of Carolina, Thirteen Colonies": "North America",
    "Southern United States (especially Louisiana and Florida)": "North America",
    "Southern United States (especially New Orleans)": "North America",
    "Thirteen Colonies": "North America",
    "Thirteen Colonies and New France, Canada": "North America",
    "United States": "North America",
    "Wyandot people, North America": "North America",

    # 🌎 South America
    "Americas": "South America",
    "Argentina": "South America",
    "Bolivia": "South America",
    "Brazil": "South America",
    "Buenos Aires, Argentina": "South America",
    "Cartagena, Colombia": "South America",
    "Central America": "South America",
    "Chile": "South America",
    "Colombia": "South America",
    "Montevideo, Uruguay": "South America",
    "Peru, Chile, Bolivia, Ecuador, Colombia, Mexico, El Salvador, Guatemala": "South America",
    "Puerto Rico, Dominican Republic, Mexico": "North America",  # Caribbean/North border
    "South America": "South America",

    # 🌏 Asia
    "Asia": "Asia",
    "Bangladesh": "Asia",
    "Bombay, India": "Asia",
    "Cambodia": "Asia",
    "China": "Asia",
    "China, Southeast Asia and Egypt": "Asia",
    "Hong Kong": "Asia",
    "India": "Asia",
    "Indonesia": "Asia",
    "Iran": "Asia",
    "Iraq": "Asia",
    "Japan": "Asia",
    "Kuala Koh, Malaysia": "Asia",
    "Malaysia": "Asia",
    "Pakistan": "Asia",
    "Persia": "Asia",
    "Peshawar, Pakistan": "Asia",
    "Philippines": "Asia",
    "Singapore": "Asia",
    "Sri Lanka": "Asia",
    "Vietnam": "Asia",
    "Yemen": "Asia",
    "Middle East": "Asia",
    "Megiddo, land of Canaan": "Asia",  # modern Israel/Levant region

    # 🌍 Europe
    "Amsterdam, Netherlands": "Europe",
    "Augsburg, Germany": "Europe",
    "Barcelona, Spain": "Europe",
    "British Isles": "Europe",
    "Cádiz, Spain": "Europe",
    "Copenhagen, Denmark": "Europe",
    "Croydon, United Kingdom": "Europe",
    "Denmark, Sweden, Lithuania": "Europe",
    "England": "Europe",
    "Europe": "Europe",
    "France": "Europe",
    "Iceland": "Europe",
    "Ireland": "Europe",
    "Italy": "Europe",
    "Lisbon, Portugal": "Europe",
    "London, England": "Europe",
    "London and Westminster, England": "Europe",
    "Malta": "Europe",
    "Messina, Sicily, Italy": "Europe",
    "Netherlands": "Europe",
    "Norfolk and Portsmouth, England": "Europe",
    "Portugal": "Europe",
    "Prague, Czech Kingdom": "Europe",
    "Romania": "Europe",
    "Rome, Byzantine Empire": "Europe",
    "Russia": "Europe",
    "Spain": "Europe",
    "Staphorst, Netherlands": "Europe",
    "Tenerife, Spain": "Europe",
    "United Kingdom": "Europe",
    "Vienna, Austria": "Europe",
    "Yugoslavia": "Europe",

    # 🌏 Oceania
    "Australia": "Oceania",
    "Fiji": "Oceania",
    "Fremantle, Western Australia": "Oceania",
    "Hawaiian Kingdom": "Oceania",
    "New South Wales, Australia": "Oceania",
    "New Zealand": "Oceania",
    "Papua New Guinea": "Oceania",
    "Queensland, Australia": "Oceania",
    "Samoa": "Oceania",
    "Sydney, Australia": "Oceania",
    "Victoria, Australia": "Oceania",

    # 🌐 Multi-region / Global
    "Asia, Africa, Europe, South America": "Multiple",
    "Asia, Africa, Europe, and Americas": "Multiple",
    "Asia, Europe": "Multiple",
    "Asia, Europe, North America": "Multiple",
    "Asia, North Africa, Europe": "Multiple",
    "Asia-Pacific, Latin America": "Multiple",
    "Byzantine Empire": "Multiple",
    "Eurasia and North Africa": "Multiple",
    "Europe and West Asia": "Multiple",
    "Europe, Asia, Africa": "Multiple",
    "Europe, North America, South America": "Multiple",
    "Ottoman Empire": "Multiple",
    "Ottoman Empire, Egypt": "Multiple",
    "Worldwide": "Global",
    "Worldwide, primarily concentrated in Guinea, Liberia, Sierra Leone": "Global",
    "Bilad al-Sham": "Asia",  # roughly Syria/Levant
    "Balkans": "Europe",
}

# --- Identify locations with unknown diseases ---
unknown_df = df[~df["Disease_Known"]]
unknown_locations = unknown_df["Location"].dropna().unique()

# print(f"\nTotal unique locations (unknown diseases): {len(unknown_locations)}\n")
# print(sorted(unknown_locations))

# --- Unknown-disease locations ---
continent_map.update({
    "Britain (England) and later continental Europe": "Europe",
    "Europe": "Europe",
    "Greece (Northern Greece, Roman Republic)": "Europe",
    "Greece, Libya, Egypt, Ethiopia": "Africa",  # spans both, Africa dominant region
    "Han Dynasty": "Asia",
    "Roman Empire": "Europe",
    "South Africa": "Africa",
    "Southern New England, British North America, especially the Wampanoag people": "North America",
})

# Add continent column
df["Continent"] = df["Location"].map(continent_map).fillna("Unknown")

# Check print
# print(df[["Location", "Continent"]].head(10))
# print(df["Continent"].value_counts())

# Death Toll data conversion
def parse_death_toll(value):
    """
    Parse a messy 'Death toll (estimate)' string and return the UPPER bound as a numeric value.
    Examples handled:
      - "5-10 million" -> 10000000
      - "75,000-100,000" -> 100000
      - "10 million" -> 10000000
      - "296 (as of 31 December 2020)" -> 296
      - "unknown" -> np.nan
    """
    if pd.isna(value):
        return np.nan

    s = str(value).lower().strip()

    # Explicit unknowns
    if any(tok in s for tok in ("unknown", "n/a", "not known", "no data")):
        return np.nan

    # Detect unit (prefer explicit words)
    unit = 1
    if re.search(r"\b(billion|bn|billion\.)\b", s):
        unit = 1_000_000_000
    elif re.search(r"\b(million|milli?on|m\b)\b", s):
        unit = 1_000_000
    elif re.search(r"\b(thousand|k\b)\b", s):
        unit = 1_000

    # Also handle compact suffixes like "10m" or "2.5k"
    suffix_match = re.search(r"([\d,.]+)\s*([mkbn])\b", s)
    if suffix_match:
        num_part = suffix_match.group(1).replace(",", "")
        suffix = suffix_match.group(2)
        try:
            val = float(num_part)
        except:
            val = None
        if val is not None:
            if suffix == "k":
                return val * 1_000
            if suffix == "m":
                return val * 1_000_000
            if suffix in ("b", "bn"):
                return val * 1_000_000_000

    # Extract numeric tokens (handles commas)
    numbers = re.findall(r"[\d]+(?:[,.\d]*\d)?", s)  # e.g. "75,000", "2.5"
    cleaned = []
    for n in numbers:
        n = n.replace(",", "")
        if n.strip():
            try:
                cleaned.append(float(n))
            except:
                pass

    if not cleaned:
        return np.nan

    # Use the UPPER bound (max)
    max_val = max(cleaned)

    # Apply the detected unit multiplier
    return max_val * unit

# Apply to your dataframe
df["Death Toll (est)"] = df["Death toll (estimate)"].apply(parse_death_toll)

coords_map = {
    # --- Americas ---
    "Americas": (15.0, -90.0),
    "North America": (40.0, -100.0),
    "South America": (-15.6, -56.1),
    "Central America": (14.5, -90.5),

    # --- Europe ---
    "Europe": (54.5260, 15.2551),
    "Western Europe": (48.5, 2.2),
    "Eastern Europe": (52.0, 21.0),
    "Northern Europe": (60.0, 15.0),
    "Southern Europe": (42.5, 12.5),

    # --- Africa ---
    "Africa": (1.5, 17.3),
    "North Africa": (26.0, 13.0),
    "East Africa": (-1.5, 37.0),
    "West Africa": (7.5, -5.0),
    "South Africa": (-30.5595, 22.9375),

    # --- Asia ---
    "Asia": (34.0479, 100.6197),
    "East Asia": (35.0, 120.0),
    "South Asia": (20.0, 78.0),
    "Southeast Asia": (10.0, 105.0),
    "West Asia": (32.0, 44.0),
    "Middle East": (29.5, 45.0),

    # --- Oceania ---
    "Australia": (-25.2744, 133.7751),
    "Oceania": (-22.7359, 140.0188),

    # --- Specific & Historical Locations ---
    "Asia, Africa, Europe, South America": (20.0, 20.0),  # generalized
    "Asia, Africa, Europe, and Americas": (20.0, 20.0),
    "Asia, Europe": (40.0, 60.0),
    "Asia, Europe, North America": (40.0, 20.0),
    "Asia, North Africa, Europe": (35.0, 25.0),
    "Asia-Pacific, Latin America": (5.0, 140.0),
    "Byzantine Empire, West Asia, Africa": (34.0, 38.0),
    "Byzantine Empire, West Asia, Syria, Mesopotamia": (35.0, 40.0),
    "Han Dynasty": (34.0, 108.0),
    "Roman Empire": (41.9, 12.5),
    "Ottoman Empire": (39.0, 35.0),
    "Greece (Northern Greece, Roman Republic)": (40.6, 22.9),
    "Greece, Libya, Egypt, Ethiopia": (24.0, 25.0),
    "Southern New England, British North America, especially the Wampanoag people": (41.7, -70.6),
    "Britain (England) and later continental Europe": (52.0, 0.0),

    # --- Modern Countries / Cities (frequent ones) ---
    "Amsterdam, Netherlands": (52.3676, 4.9041),
    "Bangladesh": (23.6850, 90.3563),
    "Brazil": (-14.2350, -51.9253),
    "China": (35.8617, 104.1954),
    "Egypt": (26.8206, 30.8025),
    "England": (52.3555, -1.1743),
    "Ethiopia": (9.1450, 40.4897),
    "France": (46.6034, 1.8883),
    "Germany": (51.1657, 10.4515),
    "Greece": (39.0742, 21.8243),
    "India": (20.5937, 78.9629),
    "Iran": (32.4279, 53.6880),
    "Italy": (41.8719, 12.5674),
    "Japan": (36.2048, 138.2529),
    "United States": (37.0902, -95.7129),
    "United Kingdom": (55.3781, -3.4360),
    "Worldwide": (0.0, 0.0),
}

# --- Map coordinates to each location ---
df["Coordinates"] = df["Location"].map(coords_map)

# Safely expand coordinates into two columns
df["Latitude"] = df["Coordinates"].apply(lambda x: x[0] if isinstance(x, (list, tuple)) else np.nan)
df["Longitude"] = df["Coordinates"].apply(lambda x: x[1] if isinstance(x, (list, tuple)) else np.nan)

# Fill missing with 0 or leave as NaN depending on your use case
df["Latitude"] = df["Latitude"].fillna(0)
df["Longitude"] = df["Longitude"].fillna(0)

# print(df[["Location", "Coordinates", "Latitude", "Longitude"]].head(15))

# --- Remove rows with unknown diseases or missing death tolls ---
df = df[(df["Disease_Known"]) & (df["Death Toll (est)"].notna())]

# --- Overwrite the original CSV with cleaned data ---
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "PandemicChronoTable.csv")
df.to_csv(data_path, index=False)
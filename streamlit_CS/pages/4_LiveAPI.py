import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

# Read API 
# Streamlit page setup
# --- Page Setup ---
st.set_page_config(page_title="Live Weather API Demo", page_icon="📡", layout="wide")

st.title("📡 Simple Weather Live Data Demo (Open-Meteo)")
st.caption("Live temperature data with auto-refresh and growing trend line.")

# --- Config ---
lat, lon = 39.7392, -104.9903  # Denver
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}

SAMPLE_DF = pd.DataFrame([
    {"time": pd.Timestamp.now(), "temperature": 20.0, "wind": 5.0}
])

# --- Cached Fetch ---
@st.cache_data(ttl=600, show_spinner=False)
def get_weather():
    """Fetch current weather safely. Returns (df, err_msg)."""
    try:
        r = requests.get(wurl, timeout=10, headers=HEADERS)
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests — try again after {retry_after}s"
        r.raise_for_status()
        j = r.json()["current"]
        df = pd.DataFrame([{
            "time": pd.to_datetime(j["time"]),
            "temperature": j["temperature_2m"],
            "wind": j["wind_speed_10m"],
        }])
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"

# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")

# Slider now supports up to 5 minutes (300 seconds)
refresh_sec = st.slider("Refresh every (sec)", 30, 300, 120)

auto_refresh = st.toggle("Enable auto-refresh", value=False)
manual_refresh = st.button("🔄 Refresh Now")

st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

if manual_refresh:
    st.cache_data.clear()
    st.toast("Data manually refreshed.", icon="🔁")

# --- Session History Setup ---
if "history" not in st.session_state:
    st.session_state["history"] = pd.DataFrame(columns=["time", "temperature", "wind"])

# --- Main View ---
st.subheader("🌤️ Live Weather Data (Denver)")

df, err = get_weather()
if err or df is None:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df = SAMPLE_DF.copy()

# Append new data point to session history
st.session_state["history"] = pd.concat(
    [st.session_state["history"], df], ignore_index=True
)

# Keep last 200 readings
st.session_state["history"] = st.session_state["history"].tail(200)

# Display latest data and trend
st.dataframe(df, use_container_width=True)

fig = px.line(
    st.session_state["history"],
    x="time",
    y="temperature",
    markers=True,
    title="Live Temperature Over Time (°C)",
    labels={"temperature": "Temperature (°C)"},
)
st.plotly_chart(fig, use_container_width=True)

# --- Auto-refresh logic ---
if auto_refresh:
    time.sleep(refresh_sec)
    st.cache_data.clear()
    st.rerun()
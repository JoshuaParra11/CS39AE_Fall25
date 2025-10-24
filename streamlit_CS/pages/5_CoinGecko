import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Live API Demo (Simple)", page_icon="📡", layout="wide")
# Disable fade/transition so charts don't blink between reruns
st.markdown(
    """
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📡 Simple Live Data Demo (CoinGecko)")
st.caption("Friendly demo with manual refresh + fallback data so it never crashes.")

# ---- Config ----
COINS = ["bitcoin", "ethereum"]
VS = "usd"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}


def build_url(ids):
    return f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies={VS}"


API_URL = build_url(COINS)

# Tiny sample to keep the demo working even if the API is rate-limiting
SAMPLE_DF = pd.DataFrame([{"coin": "bitcoin", VS: 68000}, {"coin": "ethereum", VS: 3500}])


# --- Fetch & cache ---
@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def fetch_prices(url: str):
    """Return (df, error_message). Never raise. Safe for beginners."""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        # Handle 429 and other non-200s
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests — try again after {retry_after}s"
        resp.raise_for_status()
        data = resp.json()  # e.g. {'bitcoin': {'usd': 68000}, 'ethereum': {'usd': 3500}}
        # Normalize to a simple dataframe with columns ["coin", VS]
        rows = []
        for coin, vals in data.items():
            # vals may contain multiple currencies; pick the VS key safely
            price = vals.get(VS)
            rows.append({"coin": coin, VS: price})
        df = pd.DataFrame(rows)
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"


# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")

# Let user choose how often to refresh (in seconds)
refresh_sec = st.slider("Refresh every (sec)", 10, 300, 60)  # up to 5 min if you prefer

# Toggle to turn automatic refreshing on/off
auto_refresh = st.checkbox("Enable auto-refresh", value=False)

# Manual refresh button
manual_refresh = st.button("🔄 Refresh Now")

# Show current refresh time
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

if manual_refresh:
    st.cache_data.clear()
    st.toast("Data manually refreshed.", icon="🔁")


# --- Main View ---
st.subheader("Prices")
df, err = fetch_prices(API_URL)

if err or df is None:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df = SAMPLE_DF.copy()

# Ensure the currency column exists (defensive)
if VS not in df.columns:
    df[VS] = None

st.dataframe(df, use_container_width=True)

fig = px.bar(df, x="coin", y=VS, title=f"Current price ({VS.upper()})")
st.plotly_chart(fig, use_container_width=True)

# If auto-refresh is ON, wait and rerun the app
if auto_refresh:
    time.sleep(refresh_sec)
    st.cache_data.clear()
    st.rerun()
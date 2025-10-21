import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Pie Chart", page_icon="🥧")

# Read csv
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "pie_demo.csv")
df = pd.read_csv(data_path)

# Count colors
color_counts = df.iloc[:, 0].value_counts().reset_index()
color_counts.columns = ["Color", "Count"]

# Pie Chart
st.title("Pie Chart Demo")

fig = px.pie(
    color_counts,
    names="Color",
    values="Count",
    title="Color Distribution",
    color_discrete_sequence=px.colors.qualitative.Set3
)

st.plotly_chart(fig, use_container_width=True)

options = [
    "1. Data is loaded using os to read a csv file and read using pandas.",
    "2. Counted the frequency of each color.",
    "3. Displayed results as a Plotly pie chart.",
]
st.selectbox("How was this char created?", options)
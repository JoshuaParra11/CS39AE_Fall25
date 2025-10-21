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

# Extract unique colors
unique_colors = color_counts["Color"].tolist()

# Create a mapping dictionary where the label = the color itself
color_map = {c: c.lower() for c in unique_colors}

fig = px.pie(
    color_counts,
    names="Color",
    values="Count",
    title="Color Distribution Pie Chart",
    color="Color",
    color_discrete_map=color_map
)

st.plotly_chart(fig, use_container_width=True)

# Help text
with st.expander("How is this chart created?"):
    st.write(
        """
        - Data is loaded from os and read as a csv with pandas.  
        - The frequency of each color is counted.
        - The results are displayed as a Plotly interactive pie chart.
        """
    )
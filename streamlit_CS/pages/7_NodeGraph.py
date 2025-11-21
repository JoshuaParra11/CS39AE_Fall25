import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

# Data
data = [
    ("Alice", "Bob"),
    ("Alice", "Charlie"),
    ("Bob", "Charlie"),
    ("Charlie", "Diana"),
    ("Diana", "Eve"),
    ("Bob", "Diana"),
    ("Frank", "Eve"),
    ("Eve", "Ian"),
    ("Diana", "Ian"),
    ("Ian", "Grace"),
    ("Grace", "Hannah"),
    ("Hannah", "Jack"),
    ("Charlie", "Frank"),
    ("Alice", "Eve"),
    ("Bob", "Jack")
]

# Graph construction
G = nx.DiGraph()
for name1, name2 in data:
    G.add_edge(name1, name2)

plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='purple',
        edge_color='skyblue', font_size=10, font_weight='bold')

plt.title("Lab 6.1 - Friendship Network")
st.pyplot(plt)

# Calculate degree
st.subheader("Degree Centrality (Most Connected Nodes)")

# ---- RAW DEGREE COUNT ----
degrees = dict(G.degree())
most_connected_node = max(degrees, key=degrees.get)
most_connections = degrees[most_connected_node]

st.write(f"Most connected node: **{most_connected_node}** with **{most_connections}** connections")

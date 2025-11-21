from networkx.algorithms.community import greedy_modularity_communities
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

degrees = dict(G.degree())
most_connected_node = max(degrees, key=degrees.get)
most_connections = degrees[most_connected_node]

st.write(f"Most connected node: **{most_connected_node}** with **{most_connections}** connections")

# Calculate betweeness
betweenness_centrality = nx.betweenness_centrality(G)

most_between_node = max(betweenness_centrality, key=betweenness_centrality.get)
highest_between = betweenness_centrality[most_between_node]

st.write(f"Node with highest betweenness centrality: **{most_between_node}** (score: {highest_between:.4f})")

# Calculate closeness
closeness_centrality = nx.closeness_centrality(G)

most_close_node = max(closeness_centrality, key=closeness_centrality.get)
highest_closeness = closeness_centrality[most_close_node]

st.write(f"Node with highest closeness centrality: **{most_close_node}** (score: {highest_closeness:.4f})")

# Community detection
communities = greedy_modularity_communities(G)

# Display communities in Streamlit
st.subheader("Detected Friend Groups (Communities)")
for i, community in enumerate(communities, 1):
    st.write(f"Community {i}: {list(community)}")

palette = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
node_to_comm = {}

for c_index, comm in enumerate(communities):
    for node in comm:
        node_to_comm[node] = c_index

community_colors = [palette[node_to_comm[n]] for n in G.nodes()]

plt.figure(figsize=(10, 8))
nx.draw(
    G, pos,
    with_labels=True,
    node_size=3000,
    node_color=community_colors,
    edge_color="gray",
    font_size=10,
    font_weight="bold",
    arrows=True
)

plt.title("Friendship Network Colored by Community")
st.pyplot(plt)

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

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='purple',
        edge_color='white', font_size=10, font_weight='bold')

plt.title("Lab 6.1 - Friendship Network")
plt.show()
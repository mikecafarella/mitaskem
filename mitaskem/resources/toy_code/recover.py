import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

labels = {
    "S": "SUSCEPTIBLE",
    "I": "INFECTED\nAsymptomatic\ninfected, undetected",
    "D": "DIAGNOSED\nAsymptomatic infected, detected",
    "A": "AILING\nSymptomatic\ninfected, undetected",
    "R": "RECOGNIZED\nSymptomatic infected, detected",
    "T": "THREATENED\nAcutely symptomatic infected, detected",
    "H": "HEALED",
    "E": "EXTINCT"
}

G.add_edges_from([
    ("S", "I", {"label": "Contagion\nα, β, γ, δ"}),
    ("I", "D", {"label": "Diagnosis\nε"}),
    ("I", "A", {"label": "Symptoms\nζ"}),
    ("A", "R", {"label": "Diagnosis\nθ"}),
    ("A", "E", {"label": "Death\nμ"}),
    ("R", "T", {"label": "Critical\nν"}),
    ("T", "E", {"label": "Death\nτ"}),
    ("I", "H", {"label": "Healing\nρ"}),
    ("D", "H", {"label": "Healing\nλ"}),
    ("A", "H", {"label": "Healing\nξ"}),
    ("R", "H", {"label": "Healing\nσ"}),
    ("T", "H", {"label": "Healing\nκ"})
])

pos = nx.random_layout(G, seed=42)

node_labels = {node: f"{node}\n{labels[node]}" for node in G.nodes()}
nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=2000)
edge_labels = nx.get_edge_attributes(G, "label")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.axis("off")
plt.show()
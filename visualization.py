import networkx as nx
import matplotlib.pyplot as plt

def visualize_spt(net, source, figsize=(14, 10)):
    G = nx.Graph()
    pos = {}

    # Add nodes
    for r in net.routers.values():
        G.add_node(r.id)
        pos[r.id] = (r.longitude, r.latitude)

    # Add edges
    for u in net.graph:
        for v, w in net.graph[u]:
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)

    # Build SPT edges
    router = net.routers[source]
    spt_edges = []
    for dest in net.routers:
        if dest == source:
            continue
        parent = router.parent[dest]
        if parent is not None:
            spt_edges.append((parent, dest))

    # Node colors
    node_colors = ["green" if rid == source else "lightblue" for rid in G.nodes]

    plt.figure(figsize=figsize)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=750)

    # Labels
    labels = {r.id: r.label for r in net.routers.values()}
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight="bold")

    # Topology edges
    nx.draw_networkx_edges(
        G, pos,
        edgelist=G.edges(),
        edge_color="#bbbbbb",
        width=1,
        alpha=0.8,
        connectionstyle="arc3,rad=0.12"
    )

    # SPT edges
    nx.draw_networkx_edges(
        G, pos,
        edgelist=spt_edges,
        width=3,
        edge_color="red",
        connectionstyle="arc3,rad=0.25"
    )

    # Edge labels (safe version, no custom key mapping)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=6,
        rotate=False,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.6)
    )

    plt.title(
        f"Shortest Path Tree from Router {router.label} ({router.id})",
        fontsize=16,
        fontweight="bold",
        pad=20
    )

    # Add margins
    x_vals = [p[0] for p in pos.values()]
    y_vals = [p[1] for p in pos.values()]
    plt.xlim(min(x_vals) - 2, max(x_vals) + 2)
    plt.ylim(min(y_vals) - 2, max(y_vals) + 2)

    plt.tight_layout()
    plt.show()

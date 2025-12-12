# main.py

import sys
from utils import print_network_summary, print_routing_table
from map_loader import load_graphml
from visualization import visualize_spt

def resolve_router_argument(net, arg):
    """
    Allow user to pass either:
    - router ID (int)
    - router label (string like "NY54", "CHCG")
    """
    # If numeric ID provided
    if arg.isdigit():
        rid = int(arg)
        if rid in net.routers:
            return rid

    # Otherwise search label
    for rid, r in net.routers.items():
        if r.label.lower() == arg.lower():
            return rid

    raise ValueError(f"Router '{arg}' not found by ID or label.")


def main():
    # Load dataset
    net = load_graphml("data/AttMpls.graphml.xml")
    print_network_summary(net)

    print("\n=== Computing Forwarding Tables ===")
    net.compute_all_forwarding_tables()

    # If user gave a source router argument
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        source = resolve_router_argument(net, arg)
    else:
        # Default: first router in dataset
        source = list(net.routers.keys())[0]

    print(f"\n=== Routing Table for Router {source} ({net.routers[source].label}) ===")
    print_routing_table(net, source, show_full_path=True)

    # Visualization
    print("\n=== Visualizing Shortest Path Tree ===")
    visualize_spt(net, source)


if __name__ == "__main__":
    main()

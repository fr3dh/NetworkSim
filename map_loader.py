import xml.etree.ElementTree as ET
import math
from network import Network


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance in kilometers between two points on Earth.
    """

    earthRadius = 6371

    # Convert degrees to radians for trig functions
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    lat_delta = lat2 - lat1
    lon_delta = lon2 - lon1

    # Haversine distance ()
    # a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
    # distance = 2 × R × arcsin(√a)
    a = math.sin(lat_delta / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(lon_delta / 2) ** 2
    return earthRadius * 2 * math.asin(math.sqrt(a))


def distance_to_latency(distance_km: float) -> float:
    """
    Calculate network latency (ms) based on distance in kilometers.
    Approximation: ~5ms per 1000km + 1ms base processing delay.
    """
    return round(1.0 + distance_km * 0.005, 2)


def load_graphml(filepath: str) -> Network:
    """
    Load a GraphML topology file and return a Network object.

    Args:
        filepath: Path to the .graphml file

    Returns:
        Network object with routers and links populated
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Handle XML namespace
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}

    # Parse key definitions to find attribute IDs
    keys = {}
    for key in root.findall('g:key', ns):
        attr_name = key.get('attr.name')
        key_id = key.get('id')
        keys[attr_name] = key_id

    # Get the graph element
    graph = root.find('g:graph', ns)

    # Parse nodes: extract id, label, lat, lon
    nodes = {}
    for node in graph.findall('g:node', ns):
        node_id = node.get('id')
        node_data = {'id': node_id}

        for data in node.findall('g:data', ns):
            key_id = data.get('key')
            # Match key_id to attribute name
            for attr_name, k_id in keys.items():
                if k_id == key_id:
                    node_data[attr_name] = data.text
                    break

        nodes[node_id] = node_data

    # Create Network and add routers
    net = Network()
    for node_id, data in nodes.items():
        label = data.get('label', node_id)
        net.add_router(label)
        # Store coordinates for latency calculation
        nodes[node_id]['_label'] = label

    # Parse edges and add links with latency as cost
    for edge in graph.findall('g:edge', ns):
        source_id = edge.get('source')
        target_id = edge.get('target')

        src = nodes[source_id]
        tgt = nodes[target_id]

        # Get labels (router names)
        src_label = src.get('_label', source_id)
        tgt_label = tgt.get('_label', target_id)

        # Calculate latency from coordinates
        try:
            lat1 = float(src.get('Latitude', 0))
            lon1 = float(src.get('Longitude', 0))
            lat2 = float(tgt.get('Latitude', 0))
            lon2 = float(tgt.get('Longitude', 0))

            distance = calculate_distance(lat1, lon1, lat2, lon2)
            latency = distance_to_latency(distance)
        except (ValueError, TypeError):
            latency = 10.0  # Default latency if coords missing

        # Add link (avoid duplicates for undirected graph)
        net.add_link(src_label, tgt_label, latency)

    return net


def print_network_summary(net: Network):
    """Print summary of loaded network."""
    num_routers = len(net.routers)
    num_links = sum(len(neighbors) for neighbors in net.graph.values()) // 2

    print(f"=== Network Summary ===")
    print(f"Routers: {num_routers}")
    print(f"Links: {num_links}")
    print(f"\n--- Routers ---")
    for r in net.routers:
        print(f"  {r}")
    print(f"\n--- Links ---")
    seen = set()
    for u, neighbors in net.graph.items():
        for v, cost in neighbors:
            if (v, u) not in seen:
                print(f"  {u} <-> {v}: {cost} ms")
                seen.add((u, v))


# Example usage
if __name__ == "__main__":
    # Load ATT network
    net = load_graphml("AttMpls.graphml")
    print_network_summary(net)

    print("\n=== Computing Forwarding Tables ===")
    net.compute_all_forwarding_tables()

    # Print one router's table as example
    sample_router = list(net.routers.keys())[0]
    print(f"\nForwarding table for {sample_router}:")
    for dest, nh in net.routers[sample_router].forward_table.items():
        print(f"  → {dest}: next hop = {nh}")
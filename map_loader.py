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
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Handle XML namespace
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}

    # Parse key definitions to find attribute IDs (only for nodes)
    keys = {}
    for key in root.findall('g:key', ns):
        if key.get('for') == 'node':  # Only get node attributes
            attr_name = key.get('attr.name')
            key_id = key.get('id')
            keys[key_id] = attr_name  # Changed: key_id -> attr_name

    # Get the graph element
    graph = root.find('g:graph', ns)

    # Parse nodes: extract id, label, lat, lon
    nodes = {}
    for node in graph.findall('g:node', ns):
        node_id = node.get('id')
        node_data = {'id': node_id}

        for data in node.findall('g:data', ns):
            key_id = data.get('key')
            if key_id in keys:
                attr_name = keys[key_id]
                node_data[attr_name] = data.text

        nodes[node_id] = node_data

    # Create Network and add routers with full info
    net = Network()
    for node_id, data in nodes.items():
        # Try both 'label' and 'Label' since GraphML can vary
        label = data.get('label') or data.get('Label') or node_id

        # Parse coordinates
        try:
            lat = float(data.get('Latitude', 0))
            lon = float(data.get('Longitude', 0))
        except (ValueError, TypeError):
            lat, lon = None, None

        net.add_router(
            router_id=node_id,
            label=label,
            latitude=lat,
            longitude=lon
        )

    # Parse edges and add links with latency as cost
    for edge in graph.findall('g:edge', ns):
        src_id = edge.get('source')
        tgt_id = edge.get('target')

        src = nodes[src_id]
        tgt = nodes[tgt_id]

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

        net.add_link(src_id, tgt_id, latency)

    return net


if __name__ == "__main__":
    from utils import print_network_summary, print_routing_table

    net = load_graphml("data/AttMpls.graphml.xml")
    print_network_summary(net)

    print("\n=== Computing Forwarding Tables ===")
    net.compute_all_forwarding_tables()

    # Print full path routing table for first router
    first_router = list(net.routers.keys())[0]
    print_routing_table(net, first_router, show_full_path=True)
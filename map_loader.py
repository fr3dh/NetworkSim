import xml.etree.ElementTree as ET
import math
from typing import Optional, Dict, Any, Tuple, Set
from network import Network

# Calculate the Haversine distance in kilometers between two points on Earth.
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    earthRadius = 6371.0

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    delta_latitude = lat2 - lat1
    delta_longitude = lon2 - lon1

    a = math.sin(delta_latitude / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_longitude / 2) ** 2
    return earthRadius * 2 * math.asin(math.sqrt(a))


def distance_to_latency(distance_km: float) -> float:
    """
    Calculate network latency (ms) based on distance in kilometers.
    5ms for every 1000km + 1ms base delay.
    """
    return round(1.0 + distance_km * 0.005, 2)


# Parse a float from GraphML text. Returns None for missing/invalid values.
def _parse_float_or_none(x: Any) -> Optional[float]:

    if x is None:
        return None
    s = str(x).strip()
    if s == "" or s.lower() in {"none", "null", "nan"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None

# Clean up node labels. If label is missing or "None", use fallback (node id).
def _clean_label(label: Any, fallback: str) -> str:

    if label is None:
        return fallback
    s = str(label).strip()
    if s == "" or s.lower() == "none":
        return fallback
    return s

# Fix for a common data issue
def _maybe_fix_longitude(lon: float, lat: float, assume_us_west_negative: bool) -> float:
    """
    If assume_us_west_negative is True, and a point looks like it's in the US by latitude range
    but longitude is positive, flip the sign.
    """
    if not assume_us_west_negative:
        return lon
    # Rough US latitude band
    if 15.0 <= lat <= 75.0 and lon > 0.0:
        return -lon
    return lon


def _is_valid_lat_lon(lat: Optional[float], lon: Optional[float]) -> bool:
    if lat is None or lon is None:
        return False
    return (-90.0 <= lat <= 90.0) and (-180.0 <= lon <= 180.0)

# Load a GraphML file and return a Network object.
def load_graphml(
    filepath: str,
    *,
    filter_nodes_without_geo: bool = True,
    assume_us_west_negative: bool = True,
    verbose: bool = True
) -> Network:

    tree = ET.parse(filepath)
    root = tree.getroot()

    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}

    # Build key-id -> attr.name mapping for node attributes
    key_id_to_name: Dict[str, str] = {}
    for key in root.findall("g:key", ns):
        if key.get("for") == "node":
            kid = key.get("id")
            aname = key.get("attr.name")
            if kid and aname:
                key_id_to_name[kid] = aname

    graph = root.find("g:graph", ns)
    if graph is None:
        raise ValueError("GraphML missing <graph> element.")

    # Parse all node raw data
    raw_nodes: Dict[str, Dict[str, Any]] = {}
    for node in graph.findall("g:node", ns):
        node_id = node.get("id")
        if not node_id:
            continue

        node_data: Dict[str, Any] = {"id": node_id}
        for data in node.findall("g:data", ns):
            key_id = data.get("key")
            if key_id in key_id_to_name:
                attr_name = key_id_to_name[key_id]
                node_data[attr_name] = data.text

        raw_nodes[node_id] = node_data

    # Create Network and add routers
    net = Network()

    kept_nodes: Set[str] = set()
    dropped_nodes: Set[str] = set()

    for node_id, data in raw_nodes.items():
        label = _clean_label(data.get("label") or data.get("Label"), fallback=node_id)

        lat = _parse_float_or_none(data.get("Latitude") or data.get("latitude"))
        lon = _parse_float_or_none(data.get("Longitude") or data.get("longitude"))

        if _is_valid_lat_lon(lat, lon):
            lon = _maybe_fix_longitude(lon, lat, assume_us_west_negative=assume_us_west_negative)
            net.add_router(router_id=node_id, label=label, latitude=lat, longitude=lon)
            kept_nodes.add(node_id)
        else:
            if filter_nodes_without_geo:
                dropped_nodes.add(node_id)
            else:
                # Keep the node, but without geo. Edges requiring geo will be skipped later anyway.
                net.add_router(router_id=node_id, label=label, latitude=None, longitude=None)
                kept_nodes.add(node_id)

    # Parse edges and add links with latency computed from coordinates
    total_edges = 0
    kept_edges = 0
    dropped_edges = 0
    dropped_due_to_missing_endpoint = 0
    dropped_due_to_missing_geo = 0

    for edge in graph.findall("g:edge", ns):
        total_edges += 1
        src_id = edge.get("source")
        tgt_id = edge.get("target")
        if not src_id or not tgt_id:
            dropped_edges += 1
            continue

        if src_id not in kept_nodes or tgt_id not in kept_nodes:
            dropped_edges += 1
            dropped_due_to_missing_endpoint += 1
            continue

        src = raw_nodes.get(src_id, {})
        tgt = raw_nodes.get(tgt_id, {})

        lat1 = _parse_float_or_none(src.get("Latitude") or src.get("latitude"))
        lon1 = _parse_float_or_none(src.get("Longitude") or src.get("longitude"))
        lat2 = _parse_float_or_none(tgt.get("Latitude") or tgt.get("latitude"))
        lon2 = _parse_float_or_none(tgt.get("Longitude") or tgt.get("longitude"))

        if not (_is_valid_lat_lon(lat1, lon1) and _is_valid_lat_lon(lat2, lon2)):
            dropped_edges += 1
            dropped_due_to_missing_geo += 1
            continue

        lon1 = _maybe_fix_longitude(lon1, lat1, assume_us_west_negative=assume_us_west_negative)
        lon2 = _maybe_fix_longitude(lon2, lat2, assume_us_west_negative=assume_us_west_negative)

        distance = calculate_distance(lat1, lon1, lat2, lon2)
        latency = distance_to_latency(distance)

        net.add_link(src_id, tgt_id, latency)
        kept_edges += 1

    if verbose:
        print("=== GraphML Import Summary ===")
        print(f"File: {filepath}")
        print(f"Raw nodes: {len(raw_nodes)}")
        if filter_nodes_without_geo:
            print(f"Kept nodes (with geo): {len(kept_nodes)}")
            print(f"Dropped nodes (missing/invalid geo): {len(dropped_nodes)}")
        else:
            print(f"Kept nodes (including missing geo): {len(kept_nodes)}")
            print(f"Nodes missing/invalid geo (kept but will have no geo): {sum(1 for nid in kept_nodes if nid not in dropped_nodes and (net.routers[nid].latitude is None or net.routers[nid].longitude is None))}")
        print(f"Raw edges: {total_edges}")
        print(f"Kept edges (latency computed): {kept_edges}")
        print(f"Dropped edges: {dropped_edges}")
        print(f"  - missing endpoint (filtered node): {dropped_due_to_missing_endpoint}")
        print(f"  - missing/invalid geo on endpoints: {dropped_due_to_missing_geo}")

    return net


if __name__ == "__main__":
    from utils import print_network_summary, print_routing_table

    # Julian Test
    net = load_graphml("data/Kdl.graphml", filter_nodes_without_geo=True, verbose=True)

    print_network_summary(net)

    print("\n=== Computing Forwarding Tables ===")
    net.compute_all_forwarding_tables()

    first_router = list(net.routers.keys())[0]
    print_routing_table(net, first_router, show_full_path=True)

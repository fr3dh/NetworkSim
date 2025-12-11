"""
NetworkSim - Utility Functions
Printing, visualization, and helper functions.
"""


def print_network_summary(net):
    """Print summary of loaded network."""
    num_routers = len(net.routers)
    num_links = sum(len(neighbors) for neighbors in net.graph.values()) // 2

    print(f"=== Network Summary ===")
    print(f"Routers: {num_routers}")
    print(f"Links: {num_links}")
    print(f"\n--- Routers ---")
    for router_id, router in net.routers.items():
        print(f"  {router_id} ({router.label}): ({router.latitude}, {router.longitude})")
    print(f"\n--- Links ---")
    seen = set()
    for u, neighbors in net.graph.items():
        for v, cost in neighbors:
            if (v, u) not in seen:
                u_label = net.routers[u].label
                v_label = net.routers[v].label
                print(f"  {u} ({u_label}) <-> {v} ({v_label}): {cost} ms")
                seen.add((u, v))


def print_routing_table(net, router_id, show_full_path=True):
    """Print routing table for a specific router."""
    router = net.routers[router_id]
    print(f"\nRouting table for {router.id} ({router.label}):")

    for dest in router.forward_table:
        dest_label = net.routers[dest].label

        if show_full_path:
            # Trace full path from parent pointers
            path = [dest]
            current = dest
            while router.parent[current] is not None:
                current = router.parent[current]
                path.append(current)
            path.reverse()

            path_strs = [f"{p} ({net.routers[p].label})" for p in path]
            path_str = " -> ".join(path_strs)
            print(f"  -> {dest} ({dest_label}): {path_str}  [cost: {router.dist[dest]:.2f} ms]")
        else:
            nh = router.forward_table[dest]
            nh_label = net.routers[nh].label if nh else "None"
            print(f"  -> {dest} ({dest_label}): next hop = {nh} ({nh_label})")


def print_all_routing_tables(net, show_full_path=False):
    """Print routing tables for all routers."""
    for router_id in net.routers:
        print_routing_table(net, router_id, show_full_path)
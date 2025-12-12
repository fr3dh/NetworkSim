from collections import defaultdict
from router import Router

class Network:
    def __init__(self):
        self.graph = defaultdict(list) # adjacency list
        self.routers = {} # id → Router

    def add_router(self, router_id, label=None, latitude=None, longitude=None):
        if router_id not in self.routers:
            self.routers[router_id] = Router(
                router_id,
                network=self,
                label=label,
                latitude=latitude,
                longitude=longitude
            )
        self.graph[router_id]  # 确保即使孤立点也在 graph 里

    def add_link(self, u, v, cost):
        self.graph[u].append((v, cost))
        self.graph[v].append((u, cost))

    def update_link(self, u, v, new_cost):
        self.graph[u] = [(nbr, new_cost if nbr == v else w) for nbr, w in self.graph[u]]
        self.graph[v] = [(nbr, new_cost if nbr == u else w) for nbr, w in self.graph[v]]

    def remove_link(self, u, v):
        self.graph[u] = [(nbr, w) for nbr, w in self.graph[u] if nbr != v]
        self.graph[v] = [(nbr, w) for nbr, w in self.graph[v] if nbr != u]

    def remove_router(self, router_id):
        # Remove router from graph
        for nbr in self.graph:
            self.graph[nbr] = [(n, w) for n, w in self.graph[nbr] if n != router_id]
        self.graph.pop(router_id, None)
        self.routers.pop(router_id, None)

    def compute_all_forwarding_tables(self):
        for router in self.routers.values():
            router.run_dijkstra()
            router.build_forward_table()

    def print_forwarding_tables(self):
        for r in self.routers.values():
            print(f"\nRouting table for Router {r.id}:")
            for dest, nh in r.forward_table.items():
                print(f"  → {dest}: next hop = {nh}")

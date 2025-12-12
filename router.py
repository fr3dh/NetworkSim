from dijkstra import dijkstra

class Router:
    def __init__(self, router_id, network, label=None, latitude=None, longitude=None):
        self.id = router_id
        self.label = label
        self.latitude = latitude
        self.longitude = longitude
        
        self.network = network
        
        self.dist = {}
        self.parent = {}
        self.forward_table = {}

    def run_dijkstra(self):
        graph = self.network.graph
        self.dist, self.parent = dijkstra(graph, self.id)

    def build_forward_table(self):
        self.forward_table = {}
        for dest in self.network.routers:
            if dest == self.id:
                continue
            self.forward_table[dest] = self._next_hop_to(dest)

    def _next_hop_to(self, dest):
        """Trace parent pointers backwards to find next hop."""
        if self.parent.get(dest) is None:
            return None  # unreachable or not in parent
        current = dest
        while self.parent[current] != self.id:
            current = self.parent[current]
        return current

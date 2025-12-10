import heapq

def dijkstra(graph, source):
    """
    graph: dict of {node: [(neighbor, weight), ...]}
    source: starting node
    
    returns:
        dist: shortest distances from source
        parent: parent pointers for path reconstruction
    """
    dist = {node: float('inf') for node in graph}
    parent = {node: None for node in graph}
    dist[source] = 0

    pq = [(0, source)]  # (distance, node)

    while pq:
        curr_dist, node = heapq.heappop(pq)

        # Lazy skip
        if curr_dist > dist[node]:
            continue

        # Relaxation
        for neighbor, weight in graph[node]:
            new_dist = curr_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))

    return dist, parent

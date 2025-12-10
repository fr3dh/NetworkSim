from network import Network

def main():
    net = Network()

    # Add routers
    for r in ["A", "B", "C", "D"]:
        net.add_router(r)

    # Add links
    net.add_link("A", "B", 4)
    net.add_link("A", "C", 2)
    net.add_link("C", "B", 1)
    net.add_link("B", "D", 5)
    net.add_link("C", "D", 8)

    net.compute_all_forwarding_tables()
    net.print_forwarding_tables()

    print("\n--- Simulate link failure C-B ---")
    net.remove_link("C", "B")
    net.compute_all_forwarding_tables()
    net.print_forwarding_tables()

if __name__ == "__main__":
    main()

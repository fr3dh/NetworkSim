from network import Network

def main():
    net = Network()

    net.add_router(
        router_id="R1",
        label="Chicago-1",
        latitude=41.8781,
        longitude=-87.6298
    )

    net.add_router(
        router_id="R2",
        label="NewYork-5",
        latitude=40.7128,
        longitude=-74.0060
    )

    net.add_router(
        router_id="R3",
        label="LA-Core",
        latitude=34.0522,
        longitude=-118.2437
    )

    # Add links
    net.add_link("R1", "R2", cost=12)
    net.add_link("R2", "R3", cost=20)
    net.add_link("R1", "R3", cost=30)

    net.compute_all_forwarding_tables()
    net.print_forwarding_tables()

if __name__ == "__main__":
    main()

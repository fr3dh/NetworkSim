# NetworkSim

A simple network routing simulation that uses Dijkstra's shortest path algorithm to compute forwarding tables for routers in a network.

## Overview

This project simulates a network of routers connected by links with associated costs. Each router computes its forwarding table using Dijkstra's algorithm to determine the shortest path to all other routers in the network.

## Features

- Create routers and add links between them with specified costs
- Automatically compute forwarding tables for all routers using Dijkstra's algorithm
- Handle link failures and recompute routes dynamically
- Display routing tables showing the next hop for each destination

## Project Structure

- `dijkstra.py` - Implementation of Dijkstra's shortest path algorithm
- `router.py` - Router class that computes forwarding tables using Dijkstra
- `network.py` - Network class that manages routers and links
- `main.py` - Example usage demonstrating network setup and link failure simulation

## Usage

Run the simulation:

```bash
python main.py
```

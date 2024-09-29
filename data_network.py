from concepts import Node, Resource, Link, Source
from enum import Enum
from concept_utils import get_node, print_node_details
import networkx as nx
import matplotlib.pyplot as plt


class ResourceType(Enum):
    CPU = Resource("CPU", 1.0)
    RAM = Resource("RAM", 2.0)

    def get(self) -> Resource:
        return self.value.clone()


def setup_nodes() -> list[Node]:
    return [Node("Node 1", 0.5), Node("Node 2", 0.3), Node("Node 3", 0.1)]


def setup_links(nodes: list[Node]) -> list[Link]:
    return [
        Link(get_node("Node 1", nodes), get_node("Node 2", nodes)),
        Link(get_node("Node 2", nodes), get_node("Node 3", nodes)),
    ]


def setup_sources(nodes: list[Node]) -> list[Source]:
    cpu_source = Source("CPU Generator")
    cpu_source.add_receiving_node(get_node("Node 1", nodes))
    cpu_source.add_resource_distribution(ResourceType.CPU.get(), 100)

    ram_source = Source("RAM Generator")
    ram_source.add_receiving_node(get_node("Node 2", nodes))
    ram_source.add_resource_distribution(ResourceType.RAM.get(), 200)
    return [cpu_source, ram_source]


iterations = 100
nodes = setup_nodes()
links = setup_links(nodes)
primary_node = get_node("Node 1", nodes)
sources = setup_sources(nodes)


def visualize_network(nodes, iteration):
    """Visualize the nodes and their connections, with resource counts."""
    G = nx.Graph()

    # Add nodes and their resource counts
    for node in nodes:
        G.add_node(node.name, resources=len(node.resources))

    # Add edges based on links
    for link in links:
        G.add_edge(link.first_node.name, link.second_node.name)

    # Set up node positions
    pos = nx.spring_layout(G)  # Use spring layout for positioning

    # Draw the graph
    plt.clf()
    plt.title(f"Network at Iteration {iteration}")
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="skyblue",
        node_size=[v * 500 for v in nx.get_node_attributes(G, "resources").values()],
        font_size=10,
    )

    # Add resource counts as labels
    labels = {node.name: str(len(node.resources)) for node in nodes}
    nx.draw_networkx_labels(G, pos, labels=labels, font_color="black")

    # Display plot
    plt.pause(0.1)


plt.figure(figsize=(8, 6))
plt.ion()
for i in range(iterations):
    print(f"Iteration {i + 1}:")
    for source in sources:
        source.distribute_resources()

    for node in nodes:
        node.use_resources()

    for link in links:
        link.transfer_resources()

    visualize_network(nodes, i + 1)
    print_node_details(nodes)

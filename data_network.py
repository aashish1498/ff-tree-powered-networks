import math
from concepts import Node, Resource, Link, Signal, Source, State
from enum import Enum
from concept_utils import get_node, get_source
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

grid_step = 2.2


class ResourceType(Enum):
    MASK = Resource("MASK", 1.0)
    VACCINE = Resource("VACCINE", 2.0)
    VENTILATOR = Resource("VENTILATOR", 3.0)
    SINK = Resource("SINK", -2.5)

    def get(self) -> Resource:
        return self.value.clone()


def setup_nodes() -> list[Node]:
    return [Node("Hospital A", 0.5), Node("Hospital B", 0.1), Node("Hospital C", 0.2), Node("Hospital D", 0.3)]


def get_node_positions():
    return {
        "Hospital A": (0, 0),
        "Hospital B": (grid_step, grid_step),
        "Hospital C": (grid_step, -grid_step),
        "Hospital D": (grid_step * 2, 0),
    }


def setup_links(nodes: list[Node]) -> list[Link]:
    return [
        Link(get_node("Hospital A", nodes), get_node("Hospital B", nodes), 0.8),
        Link(get_node("Hospital B", nodes), get_node("Hospital C", nodes), 0.8),
        Link(get_node("Hospital B", nodes), get_node("Hospital D", nodes)),
        Link(get_node("Hospital C", nodes), get_node("Hospital D", nodes), 0.9),
    ]


def setup_sources(nodes: list[Node]) -> list[Source]:
    source = Source("Vaccines")
    source.add_receiving_node(get_node("Hospital A", nodes))
    source.add_resource_distribution(ResourceType.VACCINE.get(), 100)
    return [source]


def add_legend():
    default_patch = mpatches.Patch(color="#87BFFF", label="Default")
    conserving_patch = mpatches.Patch(color="#CE84AD", label="Conserving Resources")
    high_expending_patch = mpatches.Patch(color="#D2E0BF", label="Expending Resources")
    plt.legend(handles=[default_patch, conserving_patch, high_expending_patch], loc="upper right", fontsize=10)


def visualize_network(nodes: list[Node], links: list[Link], sources: list[Source], iteration: int):
    if iteration == 1:
        plt.figure(figsize=(12, 8))
        plt.ion()

    G = nx.DiGraph()
    plt.clf()
    plt.title(f"Network at Iteration {iteration}")
    ax1 = plt.gca()
    ax1.set_xlim(-grid_step * 1.3, grid_step * 3.6)
    ax1.set_ylim(-grid_step * 1.3, grid_step * 2.5)
    add_legend()

    node_positions = get_node_positions()
    for node in nodes:
        if node.state == State.EXPENDING:
            color = "#D2E0BF"
        elif node.state == State.CONSERVING:
            color = "#CE84AD"
        else:
            color = "#87BFFF"

        G.add_node(node.name, pos=node_positions[node.name], size=node.effectiveness * 1.4, color=color)

    for link in links:
        transfer_amount = link.current_transfer_amount
        if transfer_amount > 0:
            G.add_edge(link.first_node.name, link.second_node.name, weight=math.log(abs(transfer_amount)))
        elif transfer_amount != 0:
            G.add_edge(link.second_node.name, link.first_node.name, weight=math.log(abs(transfer_amount)))

    for source in sources:
        color = "#DDE000"
        if source.name == "Vaccines":
            pos = (0, grid_step * 2)
        elif source.name == "Masks":
            pos = (grid_step, grid_step * 2)
        elif source.name == "Outbreak":
            pos = (2 * grid_step, -grid_step)
            color = "#F24236"
        elif source.name == "Ventilators":
            pos = (2 * grid_step, grid_step)
        G.add_node(source.name, size=3500, color=color, pos=pos)
        for receiving_node in source.receiving_nodes:
            if list(source.resource_distribution.keys())[0].value > 0:
                G.add_edge(source.name, receiving_node.name)
            else:
                G.add_edge(receiving_node.name, source.name)

    pos = nx.get_node_attributes(G, "pos")
    labels = nx.get_edge_attributes(G, "weight").values()
    node_sizes = [nx.get_node_attributes(G, "size")[node] for node in G.nodes]
    node_colors = [nx.get_node_attributes(G, "color")[node] for node in G.nodes]

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=node_sizes,
        node_color=node_colors,
        font_size=10,
        font_weight="bold",
        edge_color="#A3A3A3",
        alpha=0.7,
        width=list(labels),
    )
    plt.pause(0.005)


iterations = 300
nodes = setup_nodes()
links = setup_links(nodes)
sources = setup_sources(nodes)

for i in range(iterations):
    if i == 20:
        mask_source = Source("Masks")
        mask_source.add_receiving_node(get_node("Hospital B", nodes))
        mask_source.add_resource_distribution(ResourceType.MASK.get(), 200)
        sources.append(mask_source)
    if i == 50:
        sources.remove(get_source("Vaccines", sources))
    if i == 80:
        outbreak_source = Source("Outbreak")
        outbreak_source.add_receiving_node(get_node("Hospital C", nodes))
        outbreak_source.add_resource_distribution(ResourceType.SINK.get(), 30)
        sources.append(outbreak_source)
    if i == 110:
        get_node("Hospital C", nodes).set_signal(Signal.DANGER)
        vaccine_source = Source("Vaccines")
        vaccine_source.add_receiving_node(get_node("Hospital A", nodes))
        vaccine_source.add_resource_distribution(ResourceType.VACCINE.get(), 50)
        sources.append(vaccine_source)
    if i == 120:
        sources.remove(get_source("Masks", sources))
    if i == 170:
        sources.remove(get_source("Outbreak", sources))
    if i == 190:
        ventilator_source = Source("Ventilators")
        ventilator_source.add_receiving_node(get_node("Hospital D", nodes))
        ventilator_source.add_resource_distribution(ResourceType.VENTILATOR.get(), 20)
        sources.append(ventilator_source)
        get_node("Hospital C", nodes).set_signal(Signal.OPPORTUNITY)

    for source in sources:
        source.distribute_resources()

    for node in nodes:
        node.use_resources()

    for link in links:
        link.transfer_resources()

    if i % 2 == 0:
        visualize_network(nodes, links, sources, i + 1)

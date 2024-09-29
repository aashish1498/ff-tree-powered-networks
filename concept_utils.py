from concepts import Node, Resource, Source


def get_node(node_name: str, nodes: list[Node]) -> Node:
    for node in nodes:
        if node.name == node_name:
            return node
    return None


def get_source(source_name: str, sources: list[Source]) -> Source:
    for source in sources:
        if source.name == source_name:
            return source
    return None


def add_to_sources(
    receiving_node: Node, source_name: str, resource: Resource, amount: float, sources: list[Source]
) -> None:
    source = Source(source_name)
    source.add_receiving_node(receiving_node)
    source.add_resource_distribution(resource, amount)
    sources.append(source)


def stringify_node_resources(node: Node) -> str:
    resource_strings = []
    for resource_name, resource_list in node.resources.items():
        resource_strings.append(f"{resource_name}: {len(resource_list)}")
    return ", ".join(resource_strings)


def print_node_details(nodes: list[Node]) -> None:
    for node in nodes:
        print(
            f"{node.name} ({node.state.name}): Resources={stringify_node_resources(node)}, Effectiveness={node.effectiveness:.2f}"
        )
    print()

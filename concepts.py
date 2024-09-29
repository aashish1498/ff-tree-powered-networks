from enum import Enum


class State(Enum):
    DEFAULT = 1
    LOW_USE = 0.5
    HIGH_USE = 2


class Resource:
    name: str
    positive: bool
    value: float

    def __init__(self, name: str, value: float, positive=True):
        self.name = name
        self.value = value
        self.positive = positive

    def clone(self):
        return Resource(self.name, self.value, self.positive)


class Node:
    name: str
    resources: dict[str, list[Resource]]
    effectiveness: float = 0
    usage_rate = 0.2  # Percent of resources used per iteration
    state = State.DEFAULT

    def __init__(self, name: str, usage_rate: float):
        self.name = name
        self.usage_rate = usage_rate
        self.resources = {}

    def add_resource(self, resource: Resource):
        if resource.name not in self.resources.keys():
            self.resources[resource.name] = []
        self.resources[resource.name].append(resource)

    def use_resources(self):
        for resource_name in self.resources.keys():
            resource_list = self.resources[resource_name]
            used_resource_count = int(self.usage_rate * len(resource_list))
            for i in range(used_resource_count):
                self.effectiveness += resource_list.pop(0).value

    def retrieve_resources(self, resource_name: str, count: int) -> list[Resource]:
        retrieved_resources = []
        if resource_name in self.resources.keys():
            resource_list = self.resources[resource_name]
            for i in range(count):
                if len(resource_list) > 0:
                    retrieved_resources.append(resource_list.pop(0))
        return retrieved_resources

    def apply_state(self, state: State):
        self.state = state


class Link:
    first_node: Node
    second_node: Node
    link_effectiveness: float
    resource_gradients: dict[str, float]
    gradient_tolerance: float = 0.1

    def __init__(self, first_node: Node, second_node: Node, link_effectiveness=0.5):
        self.first_node = first_node
        self.second_node = second_node
        self.link_effectiveness = link_effectiveness
        self.resource_gradients = {}

    def set_gradients(self):
        unique_keys = set(self.first_node.resources.keys()).union(set(self.second_node.resources.keys()))
        for resource_name in unique_keys:
            self.resource_gradients[resource_name] = self.calculate_gradient(resource_name)

    def calculate_gradient(self, resource_name: str) -> float:
        first_weighted_resource = self.calculate_weighted_resource(self.first_node, resource_name)
        second_weighted_resource = self.calculate_weighted_resource(self.second_node, resource_name)
        return self.link_effectiveness * (first_weighted_resource - second_weighted_resource)

    def calculate_weighted_resource(self, node: Node, resource_name: str) -> float:
        if resource_name in node.resources.keys():
            return node.usage_rate * len(node.resources[resource_name])
        return 0

    def transfer_resources(self):
        self.set_gradients()
        for resource_name, gradient in self.resource_gradients.items():
            if gradient > 0:
                for resource in self.first_node.retrieve_resources(resource_name, int(gradient)):
                    self.second_node.add_resource(resource)
            else:
                for resource in self.second_node.retrieve_resources(resource_name, int(-gradient)):
                    self.first_node.add_resource(resource)


class Source:
    name: str
    receiving_nodes: list[Node]
    resource_distribution: dict[Resource, float]

    def __init__(self, name: str):
        self.name = name
        self.receiving_nodes = []
        self.resource_distribution = {}

    def add_receiving_node(self, node: Node):
        self.receiving_nodes.append(node)

    def add_resource_distribution(self, resource: Resource, amount: float):
        self.resource_distribution[resource] = amount

    def remove_receiving_node(self, node: Node):
        self.receiving_nodes.remove(node)

    def remove_resource_distribution(self, resource: Resource):
        if resource in self.resource_distribution.keys():
            del self.resource_distribution[resource]

    def distribute_resources(self):
        for node in self.receiving_nodes:
            for resource, amount in self.resource_distribution.items():
                for _ in range(int(amount)):
                    node.add_resource(resource.clone())

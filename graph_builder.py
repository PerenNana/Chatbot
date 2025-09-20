from langgraph.graph import StateGraph
from agent_state import State


def build_graph(nodes, edges, conditional_edges=None, entry_point=None, compile_kwargs=None):
    """
    nodes: list of tuples (name, node_fn)
    edges: list of tuples (from_node, to_node)
    conditional_edges: list of tuples (from_node, condition_fn)
    entry_point: name of entry node
    compile_kwargs: dict of kwargs for compile()
    """
    graph_builder = StateGraph(State)
    for name, node_fn in nodes:
        graph_builder.add_node(name, node_fn)
    if conditional_edges:
        for from_node, condition_fn in conditional_edges:
            graph_builder.add_conditional_edges(from_node, condition_fn)
    if entry_point:
        graph_builder.set_entry_point(entry_point)
    for from_node, to_node in edges:
        graph_builder.add_edge(from_node, to_node)
    if compile_kwargs:
        return graph_builder.compile(**compile_kwargs)
    return graph_builder.compile()

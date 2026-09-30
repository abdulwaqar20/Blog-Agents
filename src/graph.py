from langgraph.graph import StateGraph, END
from src.state import State
from src.nodes import planner, worker, reviewer
from src.router import route

def build_graph():
    g = StateGraph(State)
    g.add_node("planner", planner)
    g.add_node("worker", worker)
    g.add_node("reviewer", reviewer)

    g.set_entry_point("planner")
    g.add_edge("planner", "worker")
    g.add_edge("worker", "reviewer")
    g.add_conditional_edges("reviewer", route, {"retry": "worker", "end": END})

    return g.compile()

app = build_graph()
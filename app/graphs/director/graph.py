from langgraph.graph import StateGraph, START,END
from . import nodes, edges
from app.models import state

def build_graph():
    director = StateGraph(state.Lore)
    director.add_node("headline", nodes.generate_headline_transcript)
    director.add_node("deep_dive", nodes.generate_deep_dive)
    director.add_node("merge_audio", nodes.merge_audio)

    director.add_conditional_edges(START, edges.distribute_to_deep_dive)
    director.add_edge("headline", "merge_audio")
    director.add_edge("deep_dive", "merge_audio")
    director.add_edge("merge_audio", END)
    return director
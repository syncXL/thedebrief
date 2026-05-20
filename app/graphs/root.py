import asyncio
from app.models import state
from langgraph.graph import StateGraph, START, END
from .director import graph as director_graph
from .herald import graph as herald_graph
from .librarian import graph as librarian_graph

from .persona import graph as persona_graph
from .correspondent import graph as correspondent_graph
from . import edges

def research_article():
    sub_graph = StateGraph(state.NewsArticle)
    sub_graph.add_node("correspondent", correspondent_graph.build_graph().compile())
    sub_graph.add_node("persona", persona_graph.build_graph().compile())
    
    sub_graph.add_edge(START, "correspondent")
    sub_graph.add_edge("correspondent", "persona")
    sub_graph.add_edge("persona", END)
    return sub_graph


_researcher_graph = research_article().compile()
_sem = asyncio.Semaphore(5)

async def researcher_node(state: state.NewsArticle):
    async with _sem:
        result = await _researcher_graph.ainvoke(state)
        return {"articles": [result]}



def build_graph():
    debrief = StateGraph(state.Lore)
    debrief.add_node("inquisitor", librarian_graph.build_graph().compile())
    debrief.add_node("herald", herald_graph.build_graph().compile())
    debrief.add_node("researcher", researcher_node)  # wrapper, not compiled subgraph
    debrief.add_node("director", director_graph.build_graph().compile())

    debrief.add_edge(START, "inquisitor")
    debrief.add_edge("inquisitor", "herald")
    debrief.add_conditional_edges("herald", edges.distribute_to_researcher)
    debrief.add_edge("researcher", "director")
    debrief.add_edge("director", END)
    return debrief
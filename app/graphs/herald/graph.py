from app.models import state
from langgraph.graph import START, END, StateGraph
from . import nodes
from . import edges

def build_graph():
    herald = StateGraph(state.Lore)
    herald.add_node("start_extracting", nodes.extract_articles)
    herald.add_node("extract_article_content", nodes.extract_article_content)

    herald.add_edge(START,"start_extracting")
    herald.add_conditional_edges("start_extracting", edges.continue_to_procees_article, ["extract_article_content", END])
    herald.add_edge("extract_article_content", END)
    return herald
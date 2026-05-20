from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode,tools_condition
from . import nodes
from . import tools
from app.models import state

def build_graph():
    tool_node = ToolNode(tools=tools.get_tools())
    librarian = StateGraph(state.Lore)
    librarian.add_node("librarian", nodes.get_rss_feeds)
    librarian.add_node("tools", tool_node)

    librarian.add_edge(START, "librarian")
    librarian.add_conditional_edges("librarian", tools_condition, {"tools" : "tools", "__end__" : "__end__"})
    librarian.add_edge("tools", "librarian")
    return librarian

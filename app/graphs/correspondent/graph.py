from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from app.models import state
from . import nodes
from . import tools



def build_graph():
    correspondent = StateGraph(state.NewsArticle)
    tools_node = ToolNode(tools=tools.get_tools())
    correspondent.add_node("correspondent", nodes.research_article)
    correspondent.add_node("add_context", nodes.add_context)
    correspondent.add_node("tools", tools_node)

    correspondent.add_edge(START, "correspondent")
    correspondent.add_conditional_edges("correspondent", tools_condition,
            {"tools" : "tools", "__end__": "add_context"})
    correspondent.add_edge("tools", "correspondent")
    correspondent.add_edge("add_context", END)
    return correspondent

    
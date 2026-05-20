from app.models import state
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, END
from . import nodes
from . import states as roundtable_state
from . import tools
from . import edges


def build_persona_graph():
    persona_tools = tools.get_tools()
    persona_tools = ToolNode(tools=persona_tools)

    persona = StateGraph(state.Persona, output=roundtable_state.Personas)
    persona.add_node("run_persona", nodes.run_persona)
    persona.add_node("tools", persona_tools)
    persona.add_node("compile_persona", nodes.extract_insights)

    persona.add_edge(START, "run_persona")
    persona.add_conditional_edges("run_persona", tools_condition, {"tools" : "tools", "__end__" : "compile_persona"})
    persona.add_edge("tools", "run_persona")
    persona.add_edge("compile_persona", END)
    return persona

def build_graph():
    roundtable = StateGraph(state.NewsArticle)
    roundtable.add_node("persona_router", nodes.select_persona)
    roundtable.add_node("persona", build_persona_graph().compile())
    roundtable.add_node("prepare_historian", nodes.prepare_historian)

    roundtable.add_edge(START, "persona_router")
    roundtable.add_conditional_edges("persona_router", edges.distribute_personas)
    roundtable.add_edge("persona", "prepare_historian")
    roundtable.add_conditional_edges("prepare_historian",edges.distribute_personas)
    return roundtable

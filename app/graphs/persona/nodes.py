import logging

from app import dependencies
from app.models import state
from . import states as pr_states
from langchain_core.messages import SystemMessage, HumanMessage
from . import tools

logger = logging.getLogger(__name__)

async def select_persona(article: state.NewsArticle) -> state.NewsArticle:
    logger.info("Selecting personas for article")
    llm = dependencies.get_heavy_llm()
    instruction = dependencies.load_instruction(
        "prompts/persona/persona_router.md"
    )
    accepted_personas = tools.get_available_personas()
    logger.debug(f"Available personas: {accepted_personas}")
    persona_descs = "\n\n".join([tools.get_persona_desc(name) for name in accepted_personas])
    cur_info = tools.format_article(article["article_content"]["content"], article["context"], persona_descs)
    sys_instruct = SystemMessage(content=instruction)
    cur_info = HumanMessage(content=cur_info)
    messages = [sys_instruct, cur_info]
    personas = []
    response = await llm.ainvoke(messages, schema=pr_states.RouterOutput)
    logger.debug(f"LLM response personas: {len(response.personas)}")

    for persona in response.personas:
        name = persona.persona_id
        if name  in accepted_personas:
            reason = persona.reason
            persona_inst = {
                "name" : name,
                "reason" : reason,
                "article" : tools.format_article(article["article_content"]["content"],article["context"]),
                }
            personas.append(persona_inst)
            logger.debug(f"Added persona: {name}")
    logger.info(f"Selected {len(personas)} personas")
    return {"personas" : personas}

async def run_persona(persona : state.Persona) -> state.Persona:
    logger.info(f"Running persona: {persona['name']}")
    llm = dependencies.get_heavy_llm()
    sys_instruct = dependencies.load_instruction(
        tools.get_persona_doc_path(persona["name"]),
        reason=persona.get("reason", "")
    )
    messages = persona.get("messages",[])
    if len(messages) == 0:
        logger.debug(f"Initializing messages for persona: {persona['name']}")
        sys_instruct = SystemMessage(content=sys_instruct)
        messages = [sys_instruct, HumanMessage(content=persona["article"])]
    
    tool_to_use = tools.get_tools()
    logger.debug(f"Invoking LLM for persona: {persona['name']}")
    response = await llm.ainvoke(messages,tool_to_use)
    logger.debug(f"Completed persona: {persona['name']}")
    return {"messages" : [response]}


def extract_insights(persona: state.Persona) -> state.NewsArticle:
    logger.info(f"Extracting insights from persona: {persona['name']}")
    last_message = persona["messages"][-1]
    insight = last_message.text if hasattr(last_message, "text") else last_message.content
    persona["insight"] = insight
    logger.debug(f"Extracted insight length: {len(insight)} characters")
    return {"personas" : [persona]}

    
def prepare_historian(article: state.NewsArticle) -> state.NewsArticle:
    logger.info("Preparing historian persona")
    logger.debug(f"Number of personas with insights: {len(article['personas'])}")
    persona_insights = []
    for persona in article["personas"]:
        if persona["name"] == "historian":
            return {"personas" : []}
        persona_insights.append(tools.gen_tools.pretty_persona(persona["name"], persona["insight"]))
    persona_insights = "\n".join(persona_insights)
    full_story = tools.pretty_story(article["article_content"], article["context"],persona_insights)
    sys_instruct = dependencies.load_instruction(tools.get_persona_doc_path("historian"))
    sys_instruct = SystemMessage(content=sys_instruct)
    human_message = HumanMessage(content=full_story)
    historian_dict = {
        "name" : "historian",
        "messages" : [sys_instruct, human_message],
    }
    logger.info("Historian persona prepared successfully")
    return {
        "personas" : [historian_dict],
    }
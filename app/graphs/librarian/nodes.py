import logging

from app.models import state
from app import dependencies
from . import tools
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


async def get_rss_feeds(story: state.Lore):
    logger.debug("Entering get_rss_feeds")
    llm = dependencies.get_heavy_llm()
    countries = ", ".join(tools.get_valid_countries())
    sections = ", ".join(tools.get_valid_countries())
    continents = ", ".join(tools.get_valid_countries())
    instruction = dependencies.load_instruction("prompts/librarian/get_relevant_sources.md",
                    countries=countries,
                    sections=sections,
                    continents=continents)
    sys_msg = SystemMessage(content=instruction)
    response = await llm.ainvoke([sys_msg] + story["messages"], tools.get_tools())
    logger.debug("Exiting get_rss_feeds")
    return {"messages" : [response]}

# def verify_source(sources : state.Sources) -> state.Lore:
#     """Verify the relevance of the sources based on the user's request.
    
#     Args:
#         sources (list[Source]): A list of Source objects to be verified.
    
#     Returns:
#         list: A list of relevant sources that match the user's request.
#     """
#     selected_sources = sources["sources"][:5]
#     for source in selected_sources:
#         if (rss_data["rss_link"] == source.rss_link).sum() == 0:
#             return {"error": f"The source {source.feed_name} is not relevant to the user's request."}
#     return {"error": ""}

import logging

from rapidfuzz import process, fuzz
from langgraph.types import Command
from app import dependencies
from typing import Annotated
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage

logger = logging.getLogger(__name__)

def get_valid_countries():
    data = dependencies.get_rss_data()
    return set(data["country"].str.lower().unique())

def get_valid_sections():
    data = dependencies.get_rss_data()
    return set(data["section"].str.lower().unique())

def get_valid_continents():
    data = dependencies.get_rss_data()
    return set(data["continent"].str.lower().unique())



def fuzzy_match(query: str, valid_set: set, threshold: int = 70) -> str | None:
    """Match a query string against a set of valid values using fuzzy matching."""
    result = process.extractOne(query.lower(), valid_set, scorer=fuzz.WRatio)
    logger.debug("Fuzzy matching query=%s against %d candidates, result=%s", query, len(valid_set), result)
    if result and result[1] >= threshold:
        return result[0]
    return None


def search_rss(country: str = None, section: str = None, continent: str = None) -> list | str:
    """Search for RSS feeds based on country, section, and continent.
    Use this to explore available feeds before adding them.
    At least one argument must be provided.

    Args:
        country (str, optional): The country to search for e.g. "Nigeria", "United States".
        section (str, optional): The topic section e.g. "technology", "business", "sports".
        continent (str, optional): The continent to search for e.g. "Africa", "Europe".

    Returns:
        list: Matching RSS feeds with country, section, feed_name, rss_link, continent.
        str: Error message if no arguments provided or no matches found.
    """
    if not any([country, section, continent]):
        return "At least one of country, section, or continent must be provided."

    search_criteria = {}
    valid_countries = get_valid_countries()
    valid_sections = get_valid_sections()
    valid_continents = get_valid_continents()

    if country:
        matched = fuzzy_match(country, valid_countries)
        if not matched:
            return f"Country '{country}' not found. Valid examples: {list(valid_countries)[:8]}"
        search_criteria["country"] = matched

    if section:
        matched = fuzzy_match(section, valid_sections)
        if not matched:
            return f"Section '{section}' not found. Valid sections: {list(valid_sections)}"
        search_criteria["section"] = matched

    if continent:
        matched = fuzzy_match(continent, valid_continents)
        if not matched:
            return f"Continent '{continent}' not found. Valid continents: {list(valid_continents)}"
        search_criteria["continent"] = matched

    logger.info("Searching RSS feeds with criteria: %s", search_criteria)
    filtered_df = dependencies.get_rss_data().copy()
    logger.debug("Initial RSS feed count: %d", len(filtered_df))
    for key, value in search_criteria.items():
        filtered_df = filtered_df[filtered_df[key].str.lower() == value]
        logger.debug("Filtered by %s='%s', remaining count: %d", key, value, len(filtered_df))

    if filtered_df.empty:
        criteria_str = ", ".join(f"{k}='{v}'" for k, v in search_criteria.items())
        logger.warning("No feeds found for criteria: %s", criteria_str)
        return f"No feeds found for {criteria_str}."

    logger.info("Found %d feeds for criteria %s", len(filtered_df), search_criteria)
    output_keys = ["country", "continent", "section", "feed_name", "rss_link"]
    return filtered_df[output_keys].to_dict(orient="records")

def add_source(rss_link: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Add a verified RSS feed to the episode source list.

    Args:
        rss_link: The RSS feed URL to add.
    """
    logger.info("Attempting to add RSS source link: %s", rss_link)
    rss_data = dependencies.get_rss_data()
    match = rss_data[rss_data["rss_link"] == rss_link]

    if match.empty:
        logger.warning("No feed found with link: %s", rss_link)
        return Command(update={
            "messages": [ToolMessage(
                content=f"No feed found with link: {rss_link}",
                tool_call_id=tool_call_id
            )]
        })

    row = match.iloc[0]
    source = {
        "country" : row["country"],
        "section" : row["section"],
        "feed_name" : row["feed_name"],
        "rss_link" : row["rss_link"],
    }
    logger.info("Added RSS feed source: %s", row["feed_name"])

    return Command(update={
        "sources": [source],
        "messages": [ToolMessage(
            content=f"Added: {row['feed_name']}",
            tool_call_id=tool_call_id
        )]
    })

def get_tools():
    return [search_rss, add_source]
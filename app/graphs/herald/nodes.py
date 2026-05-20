import asyncio
import logging
from langchain_core.messages import HumanMessage
from app.models import state
from . import states as herald_states
from app import dependencies

logger = logging.getLogger(__name__)

def pretty_print_articles(articles):
    text_content = ""

    for ind, article in enumerate(articles):
        text_content += (
            f"{ind}. {article['title']}\n"
            # f"Published: {article.get('published', 'Unknown')}\n"
            # f"Summary: {article.get('summary', 'No summary')}\n\n"
        )
    return text_content


async def extract_articles(state_dict: state.Lore) -> state.Lore:
    logger.debug("Fetching recent news from %d sources", len(state_dict.get("sources", [])))
    results = await asyncio.gather(
        *[dependencies.fetch_recent_news(source["rss_link"]) for source in state_dict["sources"]],
        return_exceptions=True
    )
    all_articles = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning("Feed fetch failed: %s", result)
            continue
        all_articles.extend(result)

    all_articles = all_articles
    logger.info("Fetched %d total articles", len(all_articles))
    user_request = state_dict["messages"][0].text
    logger.info("User request %s",user_request)
    formatted_articles = pretty_print_articles(all_articles)
    logger.info("Articles %s",formatted_articles)
    if formatted_articles == "":
        logger.warning("No articles available after formatting")
        return {"articles": []}

    prompt = dependencies.load_instruction(
        "prompts/herald/article_selection.md",
        user_request=user_request,
        articles=formatted_articles,
    )
    logger.debug("Loaded article selection prompt")
    sys_msg = HumanMessage(content=prompt)
    llm = dependencies.get_heavy_llm()
    logger.info("Invoking LLM for article selection")
    response = await llm.ainvoke([sys_msg], schema=herald_states.SelectedArticles)
    logger.info("LLM returned %d selected indices", len(response.indices))
    articles = []

    for i in response.indices:
        article_content: state.ArticleContent = {
            "id": i,
            "title": all_articles[i]["title"],
            "content": all_articles[i].get("summary", ""),
            "link": all_articles[i]["link"],
        }
        articles.append({"article_content": article_content})
    logger.debug("Built %d selected article payloads", len(articles))
    return {"articles": articles}


async def extract_article_content(article: state.NewsArticle) -> state.Lore:
    link = article["article_content"]["link"]
    logger.info("Extracting content for article link: %s", link)
    parser = dependencies.get_article_parser()
    content = await parser.get_story(link)
    if not content:
        logger.warning("Skipping article with no content: %s", link)
    else:
        logger.debug("Fetched content length %d for article link %s", len(content) if content else 0, link)
    article["article_content"]["content"] = content
    logger.info("Updated article content for link: %s", link)
    return {"articles": [article]}



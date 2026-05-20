from app.models import state
from langchain_core.messages import HumanMessage
from app import dependencies
from . import tools

async def research_article(article: state.NewsArticle) -> state.NewsArticle:
    llm = dependencies.get_heavy_llm()
    messages = article["messages"]
    if len(messages) == 0:
        prompt = dependencies.load_instruction(
            "prompts/correspondent/context_extractor.md",
            title=article["article_content"]["title"],
            content=article["article_content"]["content"],
            )
        sys_msg = HumanMessage(content=prompt)
        messages = [sys_msg]

    response = await llm.ainvoke(messages, tools.get_tools())
    return {"messages" : [response]}

def add_context(article: state.NewsArticle) -> state.NewsArticle:
    messages = article["messages"]
    if len(messages) > 1:
        context = messages[-1].text
        return {"context" : context}
    return {"context" : ""}
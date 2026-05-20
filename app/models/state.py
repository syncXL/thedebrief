from langgraph.graph import MessagesState
from typing import TypedDict, List, Annotated, Any
from operator import add
from .custom_operators import merge_personas, merge_articles

class Persona(MessagesState):
    name : str
    article : str
    insight : str
    reason : str

class Source(TypedDict):
    country : str
    section : str
    feed_name: str
    rss_link : str

class Sources(TypedDict):
    sources : List[Source]



class ArticleContent(TypedDict):
    id: int
    title: str
    content: str
    link: str

class NewsArticle(MessagesState):
    article_content: ArticleContent  # clean data model
    context: str
    personas: Annotated[list[Persona], merge_personas]
    deep_dive_transcript: str
    deep_dive_data: Any


class Lore(MessagesState):
    sources : Annotated[list[Source], add]
    articles : Annotated[list[NewsArticle],merge_articles]
    headline_transcript : str
    headline_audio_data : Any
    audio_url : str
    error : str


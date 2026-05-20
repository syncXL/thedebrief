from typing import TypedDict
from app.models.state import NewsArticle

class DeepDiveSection(TypedDict):
    id : int
    total_stories : int
    story : NewsArticle
    next_story : str

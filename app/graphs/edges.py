from langgraph.types import Send
from app.models import state

def distribute_to_researcher(story : state.Lore):
    return [Send("researcher", article) for article in story["articles"]]



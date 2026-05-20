from langgraph.types import Send
from app.models import state

def continue_to_procees_article(state_dict: state.Lore):
    selected_articles = state_dict["articles"]
    if len(selected_articles) == 0:
        return "__end__"
    return [Send("extract_article_content", article) for article in selected_articles]
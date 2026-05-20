from app.models import state
from langgraph.graph import END
from langgraph.types import Send
import logging

logger = logging.getLogger(__name__)


def distribute_personas(article: state.NewsArticle):
    logger.debug("distribute_personas called for article id=%s", getattr(article, 'id', 'unknown'))
    personas = article.get("personas", [])
    logger.debug("found %d personas in article", len(personas))
    payload = []
    for idx, persona in enumerate(personas):
        insight = persona.get("insight", "nil")
        logger.debug("persona[%d] insight=%s", idx, insight)
        if insight == "nil":
            logger.info("queuing persona[%d] for send", idx)
            payload.append(Send("persona", persona))
    if len(payload) == 0:
        logger.info("no personas to send, returning END")
        return END
    logger.info("returning payload with %d items", len(payload))
    return payload


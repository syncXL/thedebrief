from app.graphs import tools as gen_tools
import uuid
from datetime import datetime


def pretty_story(content : str, context : str) -> str:
    return f"""
## ARTICLE
{content}

## CONTEXT
{context}
"""

def pretty_headline(full_episode : str):
    return f"""Here's the news for today:
    {full_episode}
    """

def current_datetime_string() -> str:
    return datetime.now().strftime("%Y/%m/%d %H:%M")

def get_expert_style_note():
    return (
    "analytical and multi-disciplinary — moves between economic, historical, "
    "legal, and human angles without announcing the shift. Direct. Has genuine "
    "opinions and doesn't hedge when the evidence is clear."
)

def generate_filename() -> str:
    ts = datetime.now().strftime('%Y%m%d')
    uid = uuid.uuid4().hex[:6]
    return f"episode_{ts}_{uid}.mp3"
# → episode_20260518_a3f2c1.mp3
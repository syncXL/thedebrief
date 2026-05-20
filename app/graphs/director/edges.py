from app.models import state
from langgraph.types import Send

def distribute_to_deep_dive(story : state.Lore):
    payloads = [Send("headline", story)]
    total_stories = len(story["articles"])
    links = []
    for ind, article in enumerate(story["articles"]):
        links.append(article["article_content"]["link"])
        entity = {
            "id" : ind + 1,
            "total_stories": total_stories,
            "story" : article,
            "next_story" : ""
            }
        if entity["id"] != total_stories:
            entity["next_story"] = story["articles"][ind+1]["article_content"]["title"]
        else:
            links = ", ".join(links)
            entity["story"]["article_content"]["content"] += f" \n Sources for the news include \n {links}"
        payload = Send("deep_dive", entity)
        payloads.append(payload)
    return payloads

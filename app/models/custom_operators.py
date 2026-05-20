
def merge_personas(existing: list, new: list) -> list:
    # new personas override existing ones by name
    existing_map = {p["name"]: p for p in existing}
    for p in new:
        existing_map[p["name"]] = p
    return list(existing_map.values())

def merge_articles(existing: list, new: list) -> list:
    existing_map = {p["article_content"]["id"]: p for p in (existing or [])}
    for p in (new or []):
        existing_map[p["article_content"]["id"]] = p
    return list(existing_map.values())
from app import dependencies

async def search(query: str) -> str:
    """Returns formatted results based on the query
    
    Args :
    query : The query to search for

    Returns:
    Formatted result
    """
    search_client = dependencies.get_search_client()
    response = await search_client.search(query)
    return response

def pretty_persona(name, insight):
    return f"""
### PERSONA
{name}

### INSIGHT
{insight}
"""


def get_tools():
    return [search]


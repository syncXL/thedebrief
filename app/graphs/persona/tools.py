from app import dependencies
from app.graphs import tools as gen_tools

def get_available_personas():
    return ["critic", "economist", "geopolitician", "lawyer", "politician", "scientist", "socialite", "tech_analyst"]

def get_persona_desc(name):
    persona_path = f"prompts/persona/{name}/desc.md"
    return dependencies.load_instruction(persona_path)

def get_persona_doc_path(name):
    return f"prompts/persona/{name}/doc.md"

def format_article(content, context, personas=None):
    if personas:
        return f"""
    ## Article
    {content}

    ## Additional Context
    {context}

    ## Available Personas
    {personas}
    """
    else:
        return f"""
    ## Article
    {content}

    ## Additional Context
    {context}"""

def pretty_story(content, context, insights):
    return f"""
## ARTICLE
{content}

## CONTEXT
{context}

## INSIGHTS
{insights}
"""

def get_tools():
    return gen_tools.get_tools()
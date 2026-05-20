import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from .graphs.librarian import graph as librarian_state_graph
from .graphs.herald import graph as herald_state_graph
from .graphs.correspondent import graph as correspondent_state_graph
from .graphs.persona import graph as persona_state_graph
from .graphs.director import graph as director_state_graph
from .graphs import root

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Compile once at module level
logger.info("Compiling librarian state graph at startup")
librarian_graph = librarian_state_graph.build_graph().compile()
herald_graph = herald_state_graph.build_graph().compile()
correspondent_graph = correspondent_state_graph.build_graph().compile()
persona_graph = persona_state_graph.build_graph().compile()
director_graph = director_state_graph.build_graph().compile()

root_graph = root.build_graph().compile()
logger.info("Librarian state graph compiled successfully")

class Episode(BaseModel):
    request: str

class GeneralRequest(BaseModel):
    request : dict

@app.post("/librarian")
async def get_librarian_insights(body: Episode):
    logger.info("Received librarian insight request")
    logger.debug("Request body: %s", body.request)
    result = await librarian_graph.ainvoke({"messages": [HumanMessage(content=body.request)]})
    logger.info("Librarian insight request processed")
    return result

@app.post("/herald")
async def get_herald_insights(body: GeneralRequest):
    logger.info("Received herald insight request")
    logger.debug("Request body: %s", body.request)
    result = await herald_graph.ainvoke(body.request)
    logger.info("Herald insight request processed")
    return result

@app.post("/correspondent")
async def get_correspondent_insights(body: GeneralRequest):
    logger.info("Received correspondent insight request")
    logger.debug("Request body: %s", body.request)
    result = await correspondent_graph.ainvoke(body.request)
    logger.info("correspondent insight request processed")
    return result

@app.post("/persona")
async def get_persona_insights(body: GeneralRequest):
    logger.info("Received persona insight request")
    logger.debug("Request body: %s", body.request)
    result = await persona_graph.ainvoke(body.request)
    logger.info("person insight request processed")
    return result

@app.post("/director")
async def get_director_insights(body: GeneralRequest):
    logger.info("Received director insight request")
    logger.debug("Request body: %s", body.request)
    result = await director_graph.ainvoke(body.request)
    result["headline_audio_data"] = Response(result["headline_audio_data"],media_type="audio/mpeg")
    for article in result["articles"]:
        article["deep_dive_data"] = Response(article["deep_dive_data"],media_type="audio/mpeg")
    logger.info("person insight request processed")
    return result


@app.post("/generate-episode")
async def generate_episode(body: Episode):
    logger.info("Received Episode request")
    logger.debug("Request body: %s", body.request)
    result = await root_graph.ainvoke({"messages": [HumanMessage(content=body.request)]})
    deep_dives = []
    for article in result["articles"]:
        article.pop("deep_dive_data")
        deep_dives.append(article)
    logger.info("Episode processed")
    return {
        "audio_url": result["audio_url"],
        "headline_transcript": result["headline_transcript"],
        "articles" : deep_dives
    }

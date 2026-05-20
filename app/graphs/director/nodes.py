import asyncio
import logging
from app.models import state
from langchain_core.messages import HumanMessage
from app import dependencies
from . import tools
from . import state as director_states

logging.basicConfig(level=logging.INFO)


async def generate_headline_transcript(story : state.Lore) -> state.Lore:
    llm = dependencies.get_max_llm()
    audio_generator = dependencies.get_tts()
    logging.info("generate_headline_transcript: starting headline generation for %d articles", len(story["articles"]))

    stories = []
    for article in story["articles"]:
        content = article["article_content"]["content"]
        context = article["context"]
        fmt_story = tools.pretty_story(content, context)
        stories.append(fmt_story)
    full_story = "\n".join(stories)
    cur_date = tools.current_datetime_string()
    headline = tools.pretty_headline(full_story)
    recency = 24
    n_story = len(story["articles"])

    headline_instruction = dependencies.load_instruction(
        "prompts/tts/highlights.md",
        date=cur_date,
        recency_hours=recency,
        n_stories=n_story,
        story_list=headline,
        expert_style_note=tools.get_expert_style_note()
    )
    logging.info("generate_headline_transcript: loaded headline instruction")

    message = HumanMessage(content=headline_instruction)
    response = await llm.ainvoke([message])
    transcript = response.text
    logging.info("generate_headline_transcript: generated transcript (%d chars)", len(transcript))

    tts_instruction = dependencies.load_instruction(
        "prompts/tts/anchor_generator.md",
        anchor_transcript=transcript
    )
    audio_data = await audio_generator.generate(tts_instruction)
    logging.info("generate_headline_transcript: generated audio data")
    return {"headline_transcript" : transcript, "headline_audio_data" : audio_data}


async def generate_deep_dive(deep_dive : director_states.DeepDiveSection) -> state.Lore:
    llm = dependencies.get_max_llm()
    audio_generator = dependencies.get_tts()
    logging.info("generate_deep_dive: starting deep dive generation for story id %s", deep_dive["id"])

    story_content = deep_dive["story"]["article_content"]["content"] 
    research_context = deep_dive["story"]["context"]
    persona_insights = []
    for insight in deep_dive["story"]["personas"]:
        fmt_insight = tools.gen_tools.pretty_persona(insight["name"], insight["insight"])
        persona_insights.append(fmt_insight)
    persona_insights = "\n".join(persona_insights)
    logging.info("generate_deep_dive: formatted %d persona insights", len(deep_dive["story"]["personas"]))
    story_id= f"{deep_dive["id"]:02d}"
    total_stories = f"{deep_dive["total_stories"]:02d}"
    position = "middle"
    if deep_dive["id"] == 1:
        position = "first"
    elif deep_dive["id"] == deep_dive["total_stories"]:
        position = "last"

    next_story = deep_dive["next_story"]

    full_message = dependencies.load_instruction(
        "prompts/tts/deep_dive.md",
        story_content=story_content,
        research_context=research_context,
        persona_insights=persona_insights,
        position=position,
        next_story_title=next_story,
        story_index=story_id,
        total_stories=total_stories
    )
    logging.info("generate_deep_dive: loaded deep dive instruction for story %s", story_id)

    response = await llm.ainvoke([HumanMessage(content=full_message)])
    deep_dive_transcript = response.text
    logging.info("generate_deep_dive: generated deep dive transcript (%d chars)", len(deep_dive_transcript))
    
    audio_prompt = dependencies.load_instruction(
        "prompts/tts/deep_dive_generator.md",
        story_index=story_id,
        deep_dive_transcript=deep_dive_transcript
    )
    audio_data = await audio_generator.generate(audio_prompt)
    logging.info("generate_deep_dive: generated deep dive audio data")
    story = deep_dive["story"]
    story["deep_dive_transcript"] = deep_dive_transcript
    story["deep_dive_data"] = audio_data
    return {"articles" : [story]}

async def merge_audio(story: state.Lore) -> state.Lore:
    audio_merger = dependencies.get_audio_merger()
    audio_storage = dependencies.get_storage()
    logging.info("merge_audio: starting merge for headline and %d deep dive audio segments", len(story["articles"]))

    audio_datas = [story["headline_audio_data"]]
    for article in story["articles"]:
        audio_datas.append(article["deep_dive_data"])

    filename = tools.generate_filename()
    logging.info("merge_audio: generated filename %s", filename)

    merged_bytes = await asyncio.to_thread(audio_merger.to_bytes, audio_datas)
    logging.info("merge_audio: merged audio bytes size %d", len(merged_bytes))
    audio_url = await audio_storage.upload(merged_bytes, filename)
    logging.info("merge_audio: uploaded merged audio to %s", audio_url)

    return {"audio_url": audio_url}
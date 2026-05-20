# app/dependencies.py
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import feedparser
from app.services.audio_merger import AudioMerger
from app.services.llm import LangchainGoogle
from app.services.tts import GeminiTTS
from app.services.audio_storage import CloudinaryStorage
from app.services import web_search
from app.services import news
from app.config import settings
from functools import lru_cache
from pathlib import Path
import pandas as pd
import asyncio

@lru_cache
def get_audio_merger() -> AudioMerger:
    return AudioMerger()

@lru_cache
def get_storage() -> CloudinaryStorage:
    return CloudinaryStorage(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
    )

@lru_cache
def get_tts() -> GeminiTTS:
    return GeminiTTS(api_key=settings.google_api_key)

@lru_cache
def get_heavy_llm() -> LangchainGoogle:
    return LangchainGoogle(settings.openrouter_api_key, "gemma-4-26b-a4b-it", True, settings.google_api_key)

@lru_cache
def get_max_llm() -> LangchainGoogle:
    return LangchainGoogle(settings.openrouter_api_key, "gemma-4-31b-it", True, settings.google_api_key)

@lru_cache
def get_rss_data() -> pd.DataFrame:
    return pd.read_csv("data/rss_feeds.csv")

@lru_cache
def get_search_client() -> web_search.WebSearch:
    return web_search.TavilySearch(api_key=settings.search_api_key)

@lru_cache
def get_article_parser():
    return news.News4k()

def load_instruction(path: str, **kwargs) -> str:
    """Read a prompt template from a file and format it with provided keyword arguments."""
    template = Path(path).read_text()
    if len(kwargs) > 0:
        return template.format(**kwargs)
    else:
        return template
    
def parse_date(date_str: str) -> datetime:
    """Parse both RFC 2822 and ISO 8601 date formats."""
    try:
        dt = parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

async def fetch_recent_news(feed_url: str, hours: int = 24) -> list:
    feed = await asyncio.to_thread(_parse_feed, feed_url)

    if feed.bozo and not feed.entries:
        print(f"[WARN] Feed parse issue for {feed_url}: {feed.bozo_exception}")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = []

    for entry in feed.entries:
        try:
            date_str = entry.get("published") or entry.get("updated")
            if not date_str:
                continue
            pub_date = parse_date(date_str)
            if pub_date >= cutoff:
                recent.append({
                    "title"    : entry.get("title", "No title"),
                    "summary"  : entry.get("summary", ""),
                    "link"     : entry.get("link", ""),
                    "published": pub_date.isoformat()
                })
        except Exception as e:
            print(f"[SKIP] Could not parse entry date: {e}")
            continue

    return recent

def _parse_feed(feed_url: str):
    feedparser.USER_AGENT = "Mozilla/5.0 (compatible; TheDebrief/1.0)"
    return feedparser.parse(feed_url)

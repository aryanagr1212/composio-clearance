"""Web search for the provider's OAuth docs.

Two providers are supported because developers already have one or the other:

- Tavily: POST https://api.tavily.com/search
- Serper: POST https://google.serper.dev/search

Adding a third provider is a new branch in `search`, not a change to the pipeline.
"""

from __future__ import annotations

from typing import Awaitable, Callable

import httpx
from pydantic import BaseModel

from app.config import Settings
from app.pipeline.errors import ResearchError

SearchFn = Callable[[str, Settings], Awaitable[list["SearchHit"]]]


class SearchHit(BaseModel):
    title: str
    url: str
    snippet: str


# Hosts that rarely contain the provider's own OAuth rules. We skip them so
# the eight-page budget is spent on docs, not on videos and social posts.
_SKIP_HOST_SUFFIXES = (
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "pinterest.com",
    "reddit.com",
    "x.com",
    "twitter.com",
)


async def search(query: str, settings: Settings) -> list[SearchHit]:
    provider = settings.resolved_search()
    if provider == "tavily":
        hits = await _tavily(query, settings.tavily_api_key or "")
    elif provider == "serper":
        hits = await _serper(query, settings.serper_api_key or "")
    else:
        raise ResearchError("No search provider is configured.")
    return _clean(hits)


def _clean(hits: list[SearchHit]) -> list[SearchHit]:
    kept: list[SearchHit] = []
    seen: set[str] = set()
    for hit in hits:
        url = hit.url.strip()
        if not url.startswith(("http://", "https://")):
            continue
        host = url.split("/")[2].lower()
        if host.startswith("www."):
            host = host[4:]
        if any(host == suffix or host.endswith("." + suffix) for suffix in _SKIP_HOST_SUFFIXES):
            continue
        if url in seen:
            continue
        seen.add(url)
        kept.append(hit.model_copy(update={"url": url}))
    return kept


async def _tavily(query: str, api_key: str) -> list[SearchHit]:
    # basic depth is the fast setting. advanced is more thorough and often
    # blows the "about a minute" budget on its own.
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 10,
        "include_answer": False,
    }
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post("https://api.tavily.com/search", json=payload)
    _raise_for_status("Tavily", response)
    body = response.json()
    hits: list[SearchHit] = []
    for item in body.get("results", []):
        hits.append(
            SearchHit(
                title=str(item.get("title") or item.get("url") or "Result"),
                url=str(item.get("url") or ""),
                snippet=str(item.get("content") or ""),
            )
        )
    return hits


async def _serper(query: str, api_key: str) -> list[SearchHit]:
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": 10},
        )
    _raise_for_status("Serper", response)
    body = response.json()
    hits: list[SearchHit] = []
    for item in body.get("organic", []):
        hits.append(
            SearchHit(
                title=str(item.get("title") or item.get("link") or "Result"),
                url=str(item.get("link") or ""),
                snippet=str(item.get("snippet") or ""),
            )
        )
    return hits


def _raise_for_status(provider: str, response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    detail = response.text[:300].replace("\n", " ")
    raise ResearchError(
        f"{provider} search failed ({response.status_code}). {detail}".strip()
    )

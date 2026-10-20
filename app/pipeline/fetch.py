"""Fetch documentation pages and reduce them to text.

Redirects are followed by hand so each hop can be rejected if it points at
a non-public address. Pages are capped so one huge marketing site cannot
crowd the model prompt.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Awaitable, Callable

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

from app.config import Settings
from app.pipeline.urls import UnsafeURL, ensure_public_http_url, join_redirect

FetchFn = Callable[[list[str], Settings], Awaitable[list["FetchedPage"]]]

USER_AGENT = "ClearanceOAuthGuide/0.1 (local research aid; docs fetch)"
MAX_BYTES = 1_000_000
MAX_CHARS = 8_000


class FetchedPage(BaseModel):
    url: str
    title: str
    text: str
    fetched_at: str


async def fetch_pages(urls: list[str], settings: Settings) -> list[FetchedPage]:
    semaphore = asyncio.Semaphore(4)
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(20.0, connect=8.0),
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,text/plain"},
        follow_redirects=False,
    ) as client:
        results = await asyncio.gather(
            *(_one(client, semaphore, url) for url in urls[: settings.max_pages])
        )
    pages = [page for page in results if page is not None]
    return pages


async def _one(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
) -> FetchedPage | None:
    async with semaphore:
        try:
            current = ensure_public_http_url(url)
            response: httpx.Response | None = None
            for _ in range(5):
                response = await client.get(current)
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("location")
                    if not location:
                        return None
                    current = ensure_public_http_url(join_redirect(current, location))
                    continue
                break
            if response is None or response.status_code >= 400:
                return None
            content_type = response.headers.get("content-type", "")
            if "html" not in content_type and "text/" not in content_type and content_type:
                return None
            raw = response.content[:MAX_BYTES]
            title, text = _to_text(raw, response.encoding or "utf-8")
            if len(text) < 200:
                return None
            return FetchedPage(
                url=str(response.url) if response.url else current,
                title=title or current,
                text=text[:MAX_CHARS],
                fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            )
        except (httpx.HTTPError, UnsafeURL, UnicodeError):
            return None


def _to_text(raw: bytes, encoding: str) -> tuple[str, str]:
    html = raw.decode(encoding, errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    main = soup.find("main") or soup.find("article")
    node = main if main and len(main.get_text(" ", strip=True)) > 400 else (soup.body or soup)
    lines = [line.strip() for line in node.get_text("\n", strip=True).splitlines()]
    text = "\n".join(line for line in lines if line)
    return title, text

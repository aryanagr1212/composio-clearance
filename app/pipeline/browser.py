"""Optional read-only look at a public page.

This is the only step that may mark a claim tested. It does not type, click,
or log in. If Playwright is not installed, the caller skips the step and says
so in the research log. A missing browser is not a failed guide.
"""

from __future__ import annotations

import asyncio

from pydantic import BaseModel

from app.pipeline.urls import UnsafeURL, ensure_public_http_url


class BrowserObservation(BaseModel):
    requested_url: str
    final_url: str
    title: str
    text_excerpt: str
    login_wall: bool
    error: str | None = None


def playwright_available() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return False
    return True


async def observe(url: str) -> BrowserObservation:
    try:
        ensure_public_http_url(url)
    except UnsafeURL as exc:
        return BrowserObservation(
            requested_url=url,
            final_url=url,
            title="",
            text_excerpt="",
            login_wall=False,
            error=str(exc),
        )
    return await asyncio.to_thread(_observe_sync, url)


def _observe_sync(url: str) -> BrowserObservation:
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20_000)
            title = page.title()
            final_url = page.url
            # Read-only: no fill, no click, no evaluate that mutates the page.
            excerpt = page.inner_text("body")[:2000]
            login_wall = page.query_selector("input[type='password']") is not None
            browser.close()
        return BrowserObservation(
            requested_url=url,
            final_url=final_url,
            title=title,
            text_excerpt=" ".join(excerpt.split()),
            login_wall=login_wall,
        )
    except Exception as exc:  # noqa: BLE001 — show a short reason, keep the guide
        return BrowserObservation(
            requested_url=url,
            final_url=url,
            title="",
            text_excerpt="",
            login_wall=False,
            error=f"{type(exc).__name__}: {exc}"[:400],
        )

"""Run one live guide from a name or a website.

Order: search, fetch a handful of pages, optionally open one public page in
a browser without touching it, then ask the model for the schema. Claims are
then downgraded until every sourced or tested sentence points at a page this
run opened. The model does not get to upgrade its own evidence.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from app.config import Settings
from app.pipeline.browser import BrowserObservation, observe, playwright_available
from app.pipeline.errors import ResearchError
from app.pipeline.extract import CompleteFn, complete_json, draft_from_model
from app.pipeline.fetch import FetchFn, FetchedPage, fetch_pages
from app.pipeline.ground import ground_guide
from app.pipeline.prompts import user_prompt
from app.pipeline.search import SearchFn, SearchHit, search
from app.schema import Guide, ResearchEvent, SourceRef
from app.store import slugify

Progress = Callable[[str], None]


async def generate_guide(
    name: str,
    website: str | None,
    settings: Settings,
    *,
    search_fn: SearchFn = search,
    fetch_fn: FetchFn = fetch_pages,
    complete: CompleteFn = complete_json,
    observe_fn: Callable[[str], "object"] = observe,
    progress: Progress | None = None,
) -> Guide:
    """Build a guide. `observe_fn` is async. The default opens Playwright."""
    settings.ensure_live_ready()
    cleaned = name.strip()
    if not cleaned:
        raise ResearchError("Enter an app name.")
    site = (website or "").strip() or None
    if site and not site.startswith(("http://", "https://")):
        site = "https://" + site

    def report(message: str) -> None:
        if progress:
            progress(message)

    report("Searching for the provider's OAuth docs")
    query = f"{cleaned} create OAuth app developer documentation scopes redirect URI app review"
    hits = await search_fn(query, settings)
    urls = _candidate_urls(site, hits, settings.max_pages)
    if not urls:
        raise ResearchError(
            f"Search returned no documentation URLs for {cleaned}. "
            "Try again with the provider's docs URL in the website field."
        )

    report(f"Reading {len(urls)} pages")
    pages = await fetch_fn(urls, settings)
    if not pages:
        raise ResearchError(
            f"Could not open any of the pages search found for {cleaned}. "
            "Check the name, or paste the provider's docs URL."
        )

    browser, browser_note = await _maybe_browse(settings, site, pages, observe_fn, report)
    report("Writing the guide from those pages")
    packet = _packet(cleaned, site, hits, pages, browser)
    draft = await draft_from_model(settings, user_prompt(cleaned, site, packet), complete)

    fetched_urls = {page.url for page in pages}
    browser_urls: set[str] = set()
    if browser and not browser.error:
        browser_urls.add(browser.final_url)
        browser_urls.add(browser.requested_url)

    guide = Guide(
        slug=slugify(draft.app_name or cleaned),
        app_name=draft.app_name or cleaned,
        homepage_url=_http(draft.homepage_url),
        docs_url=_http(draft.docs_url) or pages[0].url,
        summary=draft.summary,
        last_checked=date.today(),
        generated_by="agent",
        verdict=draft.verdict,
        requirements=draft.requirements,
        steps=draft.steps,
        scopes=draft.scopes,
        scope_advice=draft.scope_advice,
        redirect_rules=draft.redirect_rules,
        agent_can_do=draft.agent_can_do,
        human_must_do=draft.human_must_do,
        blockers=draft.blockers,
        composio=draft.composio,
        sources=[SourceRef(title=page.title, url=page.url) for page in pages],
        research_log=_log(query, hits, pages, browser, browser_note),
    )
    # Keep the permalink tied to what the developer typed, not a renamed title.
    guide.slug = slugify(cleaned)
    downgrades = ground_guide(guide, fetched_urls, browser_urls)
    for line in downgrades:
        guide.research_log.append(ResearchEvent(kind="grounding", detail=line))
    if not guide.steps:
        raise ResearchError(
            "The model returned a guide with no steps. Try again, or paste the docs URL."
        )
    return guide


def _candidate_urls(website: str | None, hits: list[SearchHit], limit: int) -> list[str]:
    urls: list[str] = []
    if website:
        urls.append(website)
    for hit in hits:
        if hit.url not in urls:
            urls.append(hit.url)
        if len(urls) >= limit:
            break
    return urls[:limit]


async def _maybe_browse(settings, website, pages, observe_fn, report: Progress) -> tuple[BrowserObservation | None, str]:
    mode = settings.browser_check
    if mode == "off":
        return None, "Browser check is off (BROWSER_CHECK=off)."
    # Tests inject their own observe function. The real one needs Playwright.
    using_default_browser = observe_fn is observe
    if using_default_browser and not playwright_available():
        if mode == "on":
            return None, "BROWSER_CHECK=on, but Playwright is not installed. Continued without it."
        return None, (
            "Browser check skipped. Playwright is not installed, so nothing "
            "in this guide is marked tested. Install it with "
            "`pip install playwright && playwright install chromium`."
        )
    target = _pick_browser_url(website, pages)
    report("Opening one public page, read-only")
    observed = await observe_fn(target)
    return observed, ""


def _pick_browser_url(website: str | None, pages: list[FetchedPage]) -> str:
    """Prefer a console-like URL, and fall back to the first page we could read.

    We do not guess a login URL that was not in the research packet. The check
    never submits a form. A login wall is a valid observation.
    """
    candidates = [page.url for page in pages]
    if website:
        candidates.insert(0, website)
    needles = ("console.", "/apps", "signup", "oauth", "developers.", "developer.")
    for url in candidates:
        if any(needle in url.lower() for needle in needles):
            return url
    return candidates[0]


def _packet(name, website, hits, pages, browser: BrowserObservation | None) -> str:
    parts = [f"App: {name}", f"Developer-supplied website: {website or 'none'}", "", "SEARCH HITS:"]
    for hit in hits[:10]:
        parts.append(f"- {hit.title} | {hit.url} | {hit.snippet[:300]}")
    parts.append("\nFETCHED PAGES:")
    for index, page in enumerate(pages, start=1):
        parts.append(f"\n--- PAGE {index} ---\nURL: {page.url}\nTITLE: {page.title}\n{page.text}")
    parts.append("\nBROWSER OBSERVATION:")
    if browser is None:
        parts.append("None. Do not use confidence tested.")
    elif browser.error:
        parts.append(f"Failed for {browser.requested_url}: {browser.error}. Do not use confidence tested.")
    else:
        parts.append(
            f"Requested: {browser.requested_url}\n"
            f"Final URL: {browser.final_url}\n"
            f"Title: {browser.title}\n"
            f"Password field visible (login wall): {browser.login_wall}\n"
            f"Visible text excerpt: {browser.text_excerpt}"
        )
    return "\n".join(parts)


def _log(query, hits, pages, browser, browser_note: str) -> list[ResearchEvent]:
    events = [
        ResearchEvent(kind="search", detail=f"Query: {query}. {len(hits)} hits kept."),
    ]
    for page in pages:
        events.append(ResearchEvent(kind="fetch", detail=page.title, url=page.url))
    if browser is None:
        events.append(ResearchEvent(kind="browser", detail=browser_note or "Browser check did not run."))
    elif browser.error:
        events.append(
            ResearchEvent(
                kind="browser",
                detail=f"Could not open {browser.requested_url}. {browser.error}",
                url=browser.requested_url,
            )
        )
    else:
        wall = "A password field was visible." if browser.login_wall else "No password field was visible."
        events.append(
            ResearchEvent(
                kind="browser",
                detail=f"Opened {browser.final_url}. Title: {browser.title}. {wall}",
                url=browser.final_url,
            )
        )
    return events


def _http(value: str | None) -> str | None:
    if value and value.startswith(("http://", "https://")):
        return value
    return None

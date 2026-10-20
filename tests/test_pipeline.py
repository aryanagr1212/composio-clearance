"""Pipeline guards: unsafe URLs, missing keys, and claim grounding."""

import asyncio
from datetime import datetime, timezone

from pydantic import ValidationError
import pytest

from app.config import Settings
from app.pipeline.errors import MissingCredentialsError
from app.pipeline.fetch import FetchedPage
from app.pipeline.generate import generate_guide
from app.pipeline.ground import ground_guide
from app.pipeline.search import SearchHit
from app.pipeline.urls import UnsafeURL, ensure_public_http_url
from app.schema import Claim, Confidence
from app.guides import load_curated


def test_missing_keys_name_the_variables():
    settings = Settings(llm_provider="auto", search_provider="auto")
    with pytest.raises(MissingCredentialsError) as caught:
        settings.ensure_live_ready()
    message = str(caught.value)
    assert "OPENAI_API_KEY" in message
    assert "TAVILY_API_KEY" in message
    assert "example guides" in message.lower()


def test_private_and_non_http_urls_are_refused():
    for url in (
        "file:///etc/passwd",
        "http://localhost/admin",
        "http://127.0.0.1/",
        "http://169.254.169.254/latest/meta-data",
        "http://10.0.0.5/",
        "http://192.168.1.1/",
    ):
        with pytest.raises(UnsafeURL):
            ensure_public_http_url(url)


def test_sourced_claim_without_a_link_is_invalid():
    with pytest.raises(ValidationError):
        Claim(text="This is sure.", confidence=Confidence.sourced)


def test_grounding_downgrades_urls_this_run_did_not_open():
    guide = load_curated()[0].model_copy(deep=True)
    claim = next(iter_claims_sourced(guide))
    claim.source_url = "https://example.com/not-opened"
    notes = ground_guide(guide, fetched_urls={"https://example.com/opened"}, browser_urls=set())
    assert claim.confidence == Confidence.uncertain
    assert claim.source_url is None
    assert notes


def test_grounding_keeps_a_fetched_source_and_a_browser_test():
    guide = load_curated()[1].model_copy(deep=True)
    sourced = next(iter_claims_sourced(guide))
    fetched = sourced.source_url
    notes = ground_guide(guide, fetched_urls={fetched}, browser_urls=set())
    assert sourced.confidence == Confidence.sourced
    assert notes  # other curated URLs were not in the tiny allow-list

    tested = Claim(
        text="The page title was Create an app.",
        confidence=Confidence.tested,
        source_url="https://example.com/console",
        note="Password field was visible.",
    )
    guide.scope_advice = tested
    notes = ground_guide(
        guide,
        fetched_urls=set(),
        browser_urls={"https://example.com/console"},
    )
    assert tested.confidence == Confidence.tested


def iter_claims_sourced(guide):
    from app.schema import iter_claims

    for claim in iter_claims(guide):
        if claim.confidence == Confidence.sourced:
            yield claim
            return


def test_live_run_with_fakes_grounds_its_claims():
    good = "https://example.com/docs/oauth"
    settings = Settings(
        openai_api_key="test-key",
        tavily_api_key="test-key",
        browser_check="off",
        data_dir="data",
    )

    async def fake_search(query, _settings):
        assert "OAuth" in query
        return [SearchHit(title="OAuth docs", url=good, snippet="Create an app")]

    async def fake_fetch(urls, _settings):
        return [
            FetchedPage(
                url=good,
                title="OAuth docs",
                text="Create an OAuth app in the developer portal. Redirect URIs must be https." * 5,
                fetched_at=datetime.now(timezone.utc).isoformat(),
            )
        ]

    async def fake_complete(_settings, _system, _user):
        return _draft(good)

    guide = asyncio.run(
        generate_guide(
            "Example CRM",
            None,
            settings,
            search_fn=fake_search,
            fetch_fn=fake_fetch,
            complete=fake_complete,
        )
    )
    assert guide.slug == "example-crm"
    assert guide.generated_by == "agent"
    texts = {claim.text: claim for claim in __import__("app.schema", fromlist=["iter_claims"]).iter_claims(guide)}
    assert texts["Redirect URIs must use https."].confidence == Confidence.sourced
    invented = texts["Review takes exactly 9 days."]
    assert invented.confidence == Confidence.uncertain
    assert any(event.kind == "grounding" for event in guide.research_log)


def _draft(good: str) -> dict:
    from app.schema import (
        Blocker,
        Claim,
        GuideDraft,
        Requirement,
        ScopeItem,
        Step,
        Verdict,
        WorkItem,
    )

    def sourced(text, url):
        return Claim(text=text, confidence="sourced", source_url=url, source_title="Docs")

    draft = GuideDraft(
        app_name="Example CRM",
        docs_url=good,
        summary="Example CRM has a self-serve OAuth app. Review timing is not in the page we opened.",
        verdict=Verdict(
            difficulty="medium",
            review_required="unknown",
            difficulty_reason=sourced("The docs describe a self-serve app form.", good),
            time_to_first_test=sourced("You create an app in the developer portal.", good),
            time_to_production=Claim(
                text="Review takes exactly 9 days.",
                confidence="sourced",
                source_url="https://blog.example.net/guess",
                source_title="A blog",
            ),
            review_summary=sourced("The page we opened does not mention a review queue.", good),
        ),
        requirements=[
            Requirement(name="Developer account", needed="required", detail=sourced("Create an app in the portal.", good))
        ],
        steps=[
            Step(
                title="Create the app",
                instructions="Open the developer portal and create an OAuth app.",
                who="human",
                console_url=good,
                detail=sourced("The docs say to create the app in the developer portal.", good),
            )
        ],
        scopes=[
            ScopeItem(
                name="read",
                tier="basic",
                triggers_review="unknown",
                purpose="Read records.",
                detail=sourced("Redirect URIs must be https.", good),
            )
        ],
        scope_advice=sourced("Request only the scopes you need.", good),
        redirect_rules=sourced("Redirect URIs must use https.", good),
        agent_can_do=[WorkItem(task="Draft the scope list.", detail=sourced("Redirect URIs must be https.", good))],
        human_must_do=[WorkItem(task="Create the app while logged in.", detail=sourced("Create an app in the developer portal.", good))],
        blockers=[
            Blocker(
                title="HTTP redirect rejected",
                what_happens=sourced("Redirect URIs must be https.", good),
                how_to_unstick="Use an https URL.",
            )
        ],
    )
    return draft.model_dump(mode="json")

"""The pages a reviewer will open, with no API keys configured."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.render import to_markdown
from app.guides import load_curated


def _client(tmp_path: Path) -> TestClient:
    settings = Settings(
        llm_provider="auto",
        search_provider="auto",
        browser_check="off",
        data_dir=tmp_path,
    )
    return TestClient(create_app(settings))


def test_home_and_examples_render_without_keys(tmp_path):
    client = _client(tmp_path)
    home = client.get("/")
    assert home.status_code == 200
    for name in ("Gmail", "Slack", "Notion", "HubSpot"):
        assert name in home.text
    assert "Live generation is off" in home.text

    gmail = client.get("/g/gmail")
    assert gmail.status_code == 200
    assert "CASA" in gmail.text
    assert "sourced" in gmail.text
    assert "uncertain" in gmail.text

    markdown = client.get("/g/gmail.md")
    assert markdown.status_code == 200
    assert "text/markdown" in markdown.headers["content-type"]
    assert "# Gmail" in markdown.text
    assert "Redirect" in markdown.text

    missing = client.get("/g/not-a-real-app")
    assert missing.status_code == 404

    listing = client.get("/api/guides")
    slugs = {item["slug"] for item in listing.json()["guides"]}
    assert {"gmail", "slack", "notion", "hubspot"} <= slugs


def test_known_app_does_not_need_keys_and_unknown_app_fails_clearly(tmp_path):
    client = _client(tmp_path)
    known = client.post("/guides", data={"name": "Gmail"}, follow_redirects=False)
    assert known.status_code == 303
    assert known.headers["location"] == "/g/gmail"

    unknown = client.post("/guides", data={"name": "Some New App"})
    assert unknown.status_code == 400
    assert "OPENAI_API_KEY" in unknown.text or "ANTHROPIC_API_KEY" in unknown.text
    assert "example guides" in unknown.text.lower()


def test_markdown_export_matches_the_guide_object():
    guide = load_curated()[2]
    text = to_markdown(guide)
    assert guide.app_name in text
    assert "## Steps" in text
    assert "## Blockers" in text
    assert "uncertain" in text

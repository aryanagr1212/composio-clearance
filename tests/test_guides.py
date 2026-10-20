"""The reviewed examples are the product. They have to load, and they have to
keep the evidence rule: a sourced or tested sentence has a link."""

from app.guides import load_curated
from app.schema import Confidence, evidence_counts, iter_claims


def test_four_examples_cover_the_difficulty_range():
    guides = {guide.slug: guide for guide in load_curated()}
    assert set(guides) == {"gmail", "slack", "notion", "hubspot"}
    assert guides["gmail"].verdict.difficulty.value == "hard"
    assert guides["slack"].verdict.difficulty.value == "easy"
    assert guides["notion"].verdict.difficulty.value == "easy"
    assert guides["hubspot"].verdict.difficulty.value == "medium"
    assert all(guide.generated_by == "curated" for guide in guides.values())


def test_every_backed_claim_has_a_link_and_each_guide_admits_a_gap():
    for guide in load_curated():
        counts = evidence_counts(guide)
        assert counts["sourced"] > 0, guide.slug
        assert counts["uncertain"] > 0, guide.slug
        for claim in iter_claims(guide):
            if claim.confidence in {Confidence.sourced, Confidence.tested}:
                assert claim.source_url and claim.source_url.startswith("https://"), claim.text
            else:
                assert claim.note, claim.text


def test_examples_name_the_blocker_a_developer_actually_hits():
    guides = {guide.slug: guide for guide in load_curated()}
    gmail = guides["gmail"].model_dump_json()
    assert "CASA" in gmail
    assert "gmail.readonly" in gmail
    slack = guides["slack"].model_dump_json()
    assert "10 weeks" in slack
    notion = guides["notion"].model_dump_json()
    assert "page picker" in notion.lower() or "Page picker" in notion or "page picker" in notion
    hubspot = guides["hubspot"].model_dump_json()
    assert "25" in hubspot

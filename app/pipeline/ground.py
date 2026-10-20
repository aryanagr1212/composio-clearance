"""Tie the model's claims back to pages this run opened.

The model is asked to cite only those pages. This pass enforces it. A sourced
claim whose URL was not opened becomes uncertain. A tested claim whose URL was
not the browser check becomes sourced, if we did fetch that URL, and uncertain
otherwise. Downgrades are written into the claim note so the guide shows its work.
"""

from __future__ import annotations

from app.pipeline.urls import canonicalize
from app.schema import Claim, Confidence, Guide, iter_claims


def ground_guide(guide: Guide, fetched_urls: set[str], browser_urls: set[str]) -> list[str]:
    """Mutate claims in place. Return one line per downgrade for the research log."""
    fetched = {_key(url) for url in fetched_urls}
    browser = {_key(url) for url in browser_urls}
    notes: list[str] = []
    for claim in iter_claims(guide):
        note = _ground_claim(claim, fetched, browser)
        if note:
            notes.append(note)
    return notes


def _ground_claim(claim: Claim, fetched: set[str], browser: set[str]) -> str | None:
    if claim.confidence == Confidence.uncertain:
        return None
    if not claim.source_url:
        return _downgrade(claim, Confidence.uncertain, "No source link was attached.")
    key = _key(claim.source_url)
    if claim.confidence == Confidence.tested:
        if key in browser:
            if not claim.note:
                claim.note = "Recorded by the read-only browser check."
            return None
        if key in fetched:
            return _downgrade(
                claim,
                Confidence.sourced,
                "Downgraded from tested. The page was fetched as text, but the browser check did not record it.",
            )
        return _downgrade(
            claim,
            Confidence.uncertain,
            "Downgraded from tested. That URL was not opened in this run.",
        )
    if key in fetched or key in browser:
        return None
    return _downgrade(
        claim,
        Confidence.uncertain,
        "Downgraded from sourced. That URL was not among the pages opened in this run.",
    )


def _downgrade(claim: Claim, confidence: Confidence, reason: str) -> str:
    original = claim.confidence.value
    claim.confidence = confidence
    claim.note = f"{reason} {claim.note}".strip() if claim.note else reason
    if confidence == Confidence.uncertain:
        # Keep the URL in the note so a reader can still look, but do not
        # present it as support we verified.
        if claim.source_url:
            claim.note = f"{claim.note} Link the model offered: {claim.source_url}"
        claim.source_url = None
        claim.source_title = None
    return f"{original} → {confidence.value}: {claim.text[:120]}"


def _key(url: str) -> str:
    try:
        return canonicalize(url)
    except ValueError:
        return url.strip()

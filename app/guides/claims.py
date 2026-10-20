"""Helpers for writing curated guides.

A curated claim should cite one page that actually says the thing. If a
sentence needs two sources, split it. If the page does not give a number,
mark the number uncertain instead of borrowing one from a blog.
"""

from __future__ import annotations

from app.schema import Claim, Confidence


def sourced(text: str, url: str, title: str, note: str | None = None) -> Claim:
    return Claim(
        text=text,
        confidence=Confidence.sourced,
        source_url=url,
        source_title=title,
        note=note,
    )


def uncertain(text: str, note: str) -> Claim:
    return Claim(text=text, confidence=Confidence.uncertain, note=note)

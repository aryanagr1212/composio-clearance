"""Guide library.

Curated guides live in code so the research notes stay next to the claims.
Generated guides are JSON files under DATA_DIR. A generated file is never
allowed to replace a curated slug: a fresh Gmail run is saved as gmail-draft
so the reviewed example stays the permalink people share.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.schema import Guide

_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"^https?://", "", text)
    text = _SLUG.sub("-", text).strip("-")
    return (text[:80] or "app")


class Library:
    def __init__(self, curated: list[Guide], data_dir: Path) -> None:
        self.data_dir = data_dir
        self.curated: dict[str, Guide] = {}
        for guide in curated:
            if guide.slug in self.curated:
                raise ValueError(f"Duplicate curated slug: {guide.slug}")
            self.curated[guide.slug] = guide
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def match_curated(self, query: str) -> Guide | None:
        key = _normalize(query)
        if not key:
            return None
        for guide in self.curated.values():
            names = {guide.slug, _normalize(guide.app_name), *(_normalize(a) for a in guide.aliases)}
            if key in names:
                return guide
        return None

    def get(self, slug: str) -> Guide | None:
        if slug in self.curated:
            return self.curated[slug]
        path = self._path(slug)
        if not path.exists():
            return None
        return Guide.model_validate_json(path.read_text(encoding="utf-8"))

    def generated_guides(self) -> list[Guide]:
        guides: list[Guide] = []
        for path in sorted(self.data_dir.glob("*.json")):
            if path.stem in self.curated:
                continue
            try:
                guides.append(Guide.model_validate_json(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return guides

    def save_generated(self, guide: Guide) -> Guide:
        """Persist a live guide. Curated slugs are rewritten to `{slug}-draft`."""
        if guide.slug in self.curated:
            guide = guide.model_copy(update={"slug": f"{guide.slug}-draft"})
        path = self._path(guide.slug)
        path.write_text(
            json.dumps(guide.model_dump(mode="json"), indent=2) + "\n",
            encoding="utf-8",
        )
        return guide

    def _path(self, slug: str) -> Path:
        safe = slugify(slug)
        return self.data_dir / f"{safe}.json"


def _normalize(value: str) -> str:
    return slugify(value).replace("-", " ").strip()

"""The guide schema.

Every factual sentence a developer might rely on is a Claim. A claim is one of:

- tested: a read-only browser check opened the page and the sentence is what
  that page showed. Curated examples are not marked tested, because nobody
  logged into a provider console while writing them.
- sourced: the sentence is backed by a URL we are willing to put next to it.
  For a live guide, that URL has to be a page this run actually opened.
- uncertain: we will not stand behind the sentence. It can still be useful
  as a lead, and the note should say what is missing.

A sourced or tested claim without a link is invalid. That rule is what keeps
a fluent model from sounding more sure than the pages it read.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Iterator, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Confidence(str, Enum):
    tested = "tested"
    sourced = "sourced"
    uncertain = "uncertain"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ReviewNeed(str, Enum):
    yes = "yes"
    no = "no"
    conditional = "conditional"
    # Used on a scope when the pages we read do not say whether it triggers review.
    unknown = "unknown"


class Need(str, Enum):
    required = "required"
    conditional = "conditional"
    optional = "optional"
    not_needed = "not_needed"


class Who(str, Enum):
    agent = "agent"
    human = "human"
    either = "either"


def _enum_lower(value: object) -> object:
    if isinstance(value, str):
        return value.strip().lower()
    return value


def _blank_to_none(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


class Claim(BaseModel):
    """One sentence a developer might act on, plus the evidence for it."""

    text: str = Field(min_length=1)
    confidence: Confidence
    source_url: str | None = None
    source_title: str | None = None
    # Why this is uncertain, or what the browser check actually saw.
    note: str | None = None

    @field_validator("confidence", mode="before")
    @classmethod
    def _confidence(cls, value: object) -> object:
        return _enum_lower(value)

    @field_validator("source_url", "source_title", "note", mode="before")
    @classmethod
    def _blanks(cls, value: object) -> object:
        return _blank_to_none(value)

    @field_validator("source_url")
    @classmethod
    def _http_source(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("source_url must be an http(s) link")
        return value

    @model_validator(mode="after")
    def evidence_rules(self) -> "Claim":
        if self.confidence in {Confidence.sourced, Confidence.tested} and not self.source_url:
            raise ValueError(f"{self.confidence.value} claims need a source_url")
        return self


class Verdict(BaseModel):
    """The four numbers a developer looks at before reading the steps."""

    difficulty: Difficulty
    review_required: ReviewNeed
    difficulty_reason: Claim
    time_to_first_test: Claim
    time_to_production: Claim
    review_summary: Claim

    @field_validator("difficulty", "review_required", mode="before")
    @classmethod
    def _enums(cls, value: object) -> object:
        return _enum_lower(value)


class Requirement(BaseModel):
    name: str = Field(min_length=1)
    needed: Need
    detail: Claim

    @field_validator("needed", mode="before")
    @classmethod
    def _needed(cls, value: object) -> object:
        return _enum_lower(value)


class Step(BaseModel):
    title: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    console_url: str | None = None
    console_label: str | None = None
    who: Who
    detail: Claim

    @field_validator("who", mode="before")
    @classmethod
    def _who(cls, value: object) -> object:
        return _enum_lower(value)

    @field_validator("console_url", "console_label", mode="before")
    @classmethod
    def _blanks(cls, value: object) -> object:
        return _blank_to_none(value)

    @field_validator("console_url")
    @classmethod
    def _http_console(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("console_url must be an http(s) link")
        return value


class ScopeItem(BaseModel):
    """A scope, capability, or permission tier. `name` is the provider's string."""

    name: str = Field(min_length=1)
    tier: str = Field(min_length=1)
    triggers_review: ReviewNeed
    purpose: str = Field(min_length=1)
    detail: Claim

    @field_validator("triggers_review", mode="before")
    @classmethod
    def _review(cls, value: object) -> object:
        return _enum_lower(value)


class WorkItem(BaseModel):
    """A recommended task. The claim is the provider fact the task is based on."""

    task: str = Field(min_length=1)
    detail: Claim


class Blocker(BaseModel):
    title: str = Field(min_length=1)
    what_happens: Claim
    how_to_unstick: str = Field(min_length=1)
    contact: str | None = None

    @field_validator("contact", mode="before")
    @classmethod
    def _contact(cls, value: object) -> object:
        return _blank_to_none(value)


class ComposioContext(BaseModel):
    """How this provider sits next to Composio managed auth. Optional on purpose."""

    managed: Claim | None = None
    custom_app: Claim | None = None


class SourceRef(BaseModel):
    title: str
    url: str


class ResearchEvent(BaseModel):
    kind: Literal["search", "fetch", "browser", "note", "grounding"]
    detail: str
    url: str | None = None


class Guide(BaseModel):
    """One shareable approval guide. Curated and live guides use the same shape."""

    schema_version: int = 1
    slug: str
    app_name: str
    aliases: list[str] = Field(default_factory=list)
    homepage_url: str | None = None
    docs_url: str | None = None
    summary: str
    last_checked: date
    generated_by: Literal["curated", "agent"]
    verdict: Verdict
    requirements: list[Requirement]
    steps: list[Step]
    scopes: list[ScopeItem]
    scope_advice: Claim
    redirect_rules: Claim
    agent_can_do: list[WorkItem]
    human_must_do: list[WorkItem]
    blockers: list[Blocker]
    composio: ComposioContext = Field(default_factory=ComposioContext)
    sources: list[SourceRef] = Field(default_factory=list)
    research_log: list[ResearchEvent] = Field(default_factory=list)

    @field_validator("homepage_url", "docs_url", mode="before")
    @classmethod
    def _urls(cls, value: object) -> object:
        return _blank_to_none(value)


class GuideDraft(BaseModel):
    """The part of a guide the model is allowed to write.

    Slug, dates, sources, and the research log are filled by the server from
    what the pipeline actually did, not from what the model claims it did.
    """

    app_name: str
    homepage_url: str | None = None
    docs_url: str | None = None
    summary: str
    verdict: Verdict
    requirements: list[Requirement] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)
    scopes: list[ScopeItem] = Field(default_factory=list)
    scope_advice: Claim
    redirect_rules: Claim
    agent_can_do: list[WorkItem] = Field(default_factory=list)
    human_must_do: list[WorkItem] = Field(default_factory=list)
    blockers: list[Blocker] = Field(default_factory=list)
    composio: ComposioContext = Field(default_factory=ComposioContext)

    @field_validator("homepage_url", "docs_url", mode="before")
    @classmethod
    def _urls(cls, value: object) -> object:
        return _blank_to_none(value)


def iter_claims(obj: object) -> Iterator[Claim]:
    """Walk a guide (or any nested model) and yield every Claim."""
    if isinstance(obj, Claim):
        yield obj
        return
    if isinstance(obj, BaseModel):
        for value in obj.__dict__.values():
            yield from iter_claims(value)
        return
    if isinstance(obj, (list, tuple)):
        for item in obj:
            yield from iter_claims(item)


def evidence_counts(guide: Guide) -> dict[str, int]:
    counts = {"tested": 0, "sourced": 0, "uncertain": 0}
    for claim in iter_claims(guide):
        counts[claim.confidence.value] += 1
    return counts


def utc_today() -> date:
    return datetime.now().date()

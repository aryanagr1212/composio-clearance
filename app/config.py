"""Environment configuration.

Live generation is deliberately strict: with no keys, the example guides still
render, and a request to research a new app fails with a message that names
the variables to set. We do not fall back to an unauthenticated scraper and
pretend that is a finished research run.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from app.pipeline.errors import MissingCredentialsError

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    llm_provider: str = "auto"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_reasoning_effort: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"
    search_provider: str = "auto"
    tavily_api_key: str | None = None
    serper_api_key: str | None = None
    browser_check: str = "auto"
    data_dir: Path = Path("data")
    max_pages: int = 8

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(ROOT / ".env")

        def clean(name: str) -> str | None:
            value = os.getenv(name, "").strip()
            return value or None

        data_dir = Path(os.getenv("DATA_DIR", "data")).expanduser()
        if not data_dir.is_absolute():
            data_dir = ROOT / data_dir
        try:
            max_pages = int(os.getenv("MAX_PAGES", "8"))
        except ValueError:
            max_pages = 8
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "auto").strip().lower() or "auto",
            openai_api_key=clean("OPENAI_API_KEY"),
            anthropic_api_key=clean("ANTHROPIC_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip() or "https://api.openai.com/v1",
            openai_reasoning_effort=clean("OPENAI_REASONING_EFFORT"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5").strip() or "claude-sonnet-4-5",
            search_provider=os.getenv("SEARCH_PROVIDER", "auto").strip().lower() or "auto",
            tavily_api_key=clean("TAVILY_API_KEY"),
            serper_api_key=clean("SERPER_API_KEY"),
            browser_check=os.getenv("BROWSER_CHECK", "auto").strip().lower() or "auto",
            data_dir=data_dir,
            max_pages=max(1, min(max_pages, 12)),
        )

    def resolved_llm(self) -> str | None:
        """Which model provider this process will call, or None if it cannot."""
        choice = self.llm_provider
        if choice == "openai":
            return "openai" if self.openai_api_key else None
        if choice == "anthropic":
            return "anthropic" if self.anthropic_api_key else None
        if self.openai_api_key:
            return "openai"
        if self.anthropic_api_key:
            return "anthropic"
        return None

    def resolved_search(self) -> str | None:
        choice = self.search_provider
        if choice == "tavily":
            return "tavily" if self.tavily_api_key else None
        if choice == "serper":
            return "serper" if self.serper_api_key else None
        if self.tavily_api_key:
            return "tavily"
        if self.serper_api_key:
            return "serper"
        return None

    def live_ready(self) -> bool:
        return self.resolved_llm() is not None and self.resolved_search() is not None

    def missing_live_requirements(self) -> list[str]:
        missing: list[str] = []
        if self.resolved_llm() is None:
            if self.llm_provider == "openai":
                missing.append("OPENAI_API_KEY (LLM_PROVIDER is openai)")
            elif self.llm_provider == "anthropic":
                missing.append("ANTHROPIC_API_KEY (LLM_PROVIDER is anthropic)")
            else:
                missing.append("an LLM key (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        if self.resolved_search() is None:
            if self.search_provider == "tavily":
                missing.append("TAVILY_API_KEY (SEARCH_PROVIDER is tavily)")
            elif self.search_provider == "serper":
                missing.append("SERPER_API_KEY (SEARCH_PROVIDER is serper)")
            else:
                missing.append("a search key (TAVILY_API_KEY or SERPER_API_KEY)")
        return missing

    def ensure_live_ready(self) -> None:
        missing = self.missing_live_requirements()
        if not missing:
            return
        raise MissingCredentialsError(
            "Live generation is off until you set "
            + " and ".join(missing)
            + ". Copy .env.example to .env, fill in the keys, and restart the server. "
            "The example guides do not need keys."
        )

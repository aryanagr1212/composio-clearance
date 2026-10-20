"""HTTP UI and JSON API.

Example guides are ordinary pages. Live generation is a background job so the
browser can show which stage is running. Jobs live in memory; a restart drops
in-flight work. Finished guides are files under DATA_DIR and survive a restart.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.guides import load_curated
from app.pipeline.errors import GuideError, MissingCredentialsError
from app.pipeline.extract import _KEY_RE
from app.pipeline.generate import generate_guide
from app.render import to_markdown
from app.schema import evidence_counts
from app.store import Library, slugify

WEB = Path(__file__).resolve().parent / "web"
templates = Jinja2Templates(directory=str(WEB / "templates"))
templates.env.filters["label"] = lambda value: str(value).replace("_", " ")


@dataclass
class Job:
    id: str
    name: str
    status: str = "running"
    stage: str = "Starting"
    slug: str | None = None
    error: str | None = None
    started: float = field(default_factory=time.time)

    def public(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "stage": self.stage,
            "slug": self.slug,
            "error": self.error,
            "elapsed_seconds": round(time.time() - self.started, 1),
        }


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="Clearance", docs_url="/api/docs")
    app.state.settings = settings
    app.state.library = Library(load_curated(), settings.data_dir)
    app.state.jobs: dict[str, Job] = {}
    app.mount("/static", StaticFiles(directory=str(WEB / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        library: Library = request.app.state.library
        return templates.TemplateResponse(
            request,
            "home.html",
            {
                "curated": list(library.curated.values()),
                "generated": library.generated_guides(),
                "live_ready": settings.live_ready(),
                "live_gap": settings.missing_live_requirements(),
            },
        )

    @app.post("/guides")
    async def start(
        request: Request,
        name: str = Form(...),
        website: str = Form(""),
        fresh: str = Form(""),
    ):
        library: Library = request.app.state.library
        curated = library.match_curated(name)
        if curated and fresh != "1":
            return RedirectResponse(f"/g/{curated.slug}", status_code=303)
        try:
            settings.ensure_live_ready()
        except MissingCredentialsError as exc:
            return templates.TemplateResponse(
                request,
                "unavailable.html",
                {"message": str(exc), "name": name},
                status_code=400,
            )
        store_slug = _store_slug(library, name)
        if fresh != "1":
            existing = library.get(store_slug)
            if existing and existing.generated_by == "agent":
                return RedirectResponse(f"/g/{existing.slug}", status_code=303)
        job = Job(id=uuid.uuid4().hex[:12], name=name.strip())
        request.app.state.jobs[job.id] = job
        # The task updates job.stage as the pipeline moves. The job page polls it.
        asyncio.create_task(_run_job(job, name.strip(), website.strip(), settings, library))
        return RedirectResponse(f"/jobs/{job.id}", status_code=303)

    @app.get("/jobs/{job_id}", response_class=HTMLResponse)
    def job_page(request: Request, job_id: str) -> HTMLResponse:
        job = request.app.state.jobs.get(job_id)
        if job is None:
            return templates.TemplateResponse(
                request,
                "missing.html",
                {"slug": job_id, "kind": "job"},
                status_code=404,
            )
        return templates.TemplateResponse(request, "job.html", {"job": job})

    @app.get("/api/jobs/{job_id}")
    def job_json(request: Request, job_id: str) -> dict:
        job = request.app.state.jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="That job is not on this server.")
        return job.public()

    @app.get("/g/{slug}.md", response_class=PlainTextResponse)
    def guide_markdown(request: Request, slug: str) -> PlainTextResponse:
        guide = request.app.state.library.get(slug)
        if guide is None:
            raise HTTPException(status_code=404, detail="No guide with that name.")
        return PlainTextResponse(to_markdown(guide), media_type="text/markdown; charset=utf-8")

    @app.get("/g/{slug}", response_class=HTMLResponse)
    def guide_page(request: Request, slug: str) -> HTMLResponse:
        guide = request.app.state.library.get(slug)
        if guide is None:
            return templates.TemplateResponse(
                request,
                "missing.html",
                {"slug": slug, "kind": "guide"},
                status_code=404,
            )
        return templates.TemplateResponse(
            request,
            "guide.html",
            {
                "guide": guide,
                "counts": evidence_counts(guide),
                "live_ready": settings.live_ready(),
            },
        )

    @app.get("/api/guides")
    def list_guides(request: Request) -> dict:
        library: Library = request.app.state.library
        guides = list(library.curated.values()) + library.generated_guides()
        return {
            "guides": [
                {
                    "slug": guide.slug,
                    "app_name": guide.app_name,
                    "difficulty": guide.verdict.difficulty.value,
                    "review_required": guide.verdict.review_required.value,
                    "generated_by": guide.generated_by,
                    "last_checked": guide.last_checked.isoformat(),
                    "url": f"/g/{guide.slug}",
                }
                for guide in guides
            ]
        }

    @app.get("/api/guides/{slug}")
    def guide_json(request: Request, slug: str) -> dict:
        guide = request.app.state.library.get(slug)
        if guide is None:
            raise HTTPException(status_code=404, detail="No guide with that name.")
        payload = guide.model_dump(mode="json")
        payload["evidence"] = evidence_counts(guide)
        return payload

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "live_ready": settings.live_ready()}

    return app


def _store_slug(library: Library, name: str) -> str:
    slug = slugify(name)
    if slug in library.curated:
        return f"{slug}-draft"
    return slug


async def _run_job(job: Job, name: str, website: str, settings: Settings, library: Library) -> None:
    try:
        guide = await generate_guide(
            name,
            website or None,
            settings,
            progress=lambda message: setattr(job, "stage", message),
        )
        saved = library.save_generated(guide)
        job.slug = saved.slug
        job.status = "done"
        job.stage = "Saved"
    except GuideError as exc:
        job.status = "error"
        job.error = str(exc)
        job.stage = "Stopped"
    except Exception as exc:  # noqa: BLE001 — last-resort message for the job page
        job.status = "error"
        job.stage = "Stopped"
        job.error = _KEY_RE.sub(
            "[redacted]",
            f"Unexpected failure ({type(exc).__name__}): {exc}"[:500],
        )


app = create_app()

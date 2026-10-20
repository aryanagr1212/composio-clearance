"""Markdown export. The HTML page is a separate template over the same Guide."""

from __future__ import annotations

from app.schema import Claim, Guide, evidence_counts


def to_markdown(guide: Guide) -> str:
    counts = evidence_counts(guide)
    verdict = guide.verdict
    lines = [
        f"# {guide.app_name} OAuth approval guide",
        "",
        f"Difficulty: **{verdict.difficulty.value.title()}**. "
        f"Review: **{verdict.review_required.value}**. "
        f"Last checked: {guide.last_checked.isoformat()}. "
        f"Origin: {guide.generated_by}.",
        "",
        (
            f"Evidence: {counts['tested']} tested, {counts['sourced']} sourced, "
            f"{counts['uncertain']} uncertain."
        ),
        "",
        guide.summary,
        "",
        "## Verdict",
        "",
        f"- How hard: {_claim(verdict.difficulty_reason)}",
        f"- Time to a first test call: {_claim(verdict.time_to_first_test)}",
        f"- Time to production approval: {_claim(verdict.time_to_production)}",
        f"- Is review required: {_claim(verdict.review_summary)}",
        "",
        "## Requirements",
        "",
    ]
    for item in guide.requirements:
        lines.append(f"- **{item.name}** ({item.needed.value}): {_claim(item.detail)}")
    lines += ["", "## Steps", ""]
    for index, step in enumerate(guide.steps, start=1):
        who = {"agent": "Agent", "human": "You", "either": "Either"}[step.who.value]
        lines.append(f"### {index}. {step.title}")
        lines.append("")
        lines.append(f"Who: {who}.")
        lines.append("")
        lines.append(step.instructions)
        lines.append("")
        if step.console_url:
            label = step.console_label or step.console_url
            lines.append(f"Open: [{label}]({step.console_url})")
            lines.append("")
        lines.append(_claim(step.detail))
        lines.append("")
    lines += ["## Scopes", ""]
    for scope in guide.scopes:
        lines.append(
            f"- `{scope.name}` — {scope.tier}, review {scope.triggers_review.value}. "
            f"{scope.purpose} {_claim(scope.detail)}"
        )
    lines += [
        "",
        f"Scope advice: {_claim(guide.scope_advice)}",
        "",
        "## Redirect URIs",
        "",
        _claim(guide.redirect_rules),
        "",
        "## What an agent can prepare",
        "",
    ]
    for item in guide.agent_can_do:
        lines.append(f"- **{item.task}** {_claim(item.detail)}")
    lines += ["", "## What you have to do", ""]
    for item in guide.human_must_do:
        lines.append(f"- **{item.task}** {_claim(item.detail)}")
    lines += ["", "## Blockers", ""]
    for blocker in guide.blockers:
        lines.append(f"### {blocker.title}")
        lines.append("")
        lines.append(_claim(blocker.what_happens))
        lines.append("")
        lines.append(blocker.how_to_unstick)
        if blocker.contact:
            lines.append("")
            lines.append(f"Contact: {blocker.contact}")
        lines.append("")
    if guide.composio.managed or guide.composio.custom_app:
        lines += ["## If you are using Composio", ""]
        if guide.composio.managed:
            lines.append(f"- Managed auth: {_claim(guide.composio.managed)}")
        if guide.composio.custom_app:
            lines.append(f"- Your own OAuth app: {_claim(guide.composio.custom_app)}")
        lines.append("")
    if guide.sources:
        lines += ["## Pages this guide used", ""]
        for source in guide.sources:
            lines.append(f"- [{source.title}]({source.url})")
        lines.append("")
    if guide.research_log:
        lines += ["## How this guide was made", ""]
        for event in guide.research_log:
            suffix = f" ({event.url})" if event.url else ""
            lines.append(f"- {event.kind}: {event.detail}{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _claim(claim: Claim) -> str:
    label = claim.confidence.value
    if claim.source_url:
        title = claim.source_title or claim.source_url
        evidence = f"[{label}]({claim.source_url} \"{title}\")"
    else:
        evidence = label
    note = f" ({claim.note})" if claim.note else ""
    return f"{claim.text} _{evidence}_{note}"

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_ACTIVE_TRACK_GUARDRAILS_PASS"

REQUIRED_PHRASES = {
    "docs/ACTIVE_TRACK_GUARDRAILS.md": (
        "The active project direction is runtime terrain quality",
        "Human-visible review is a final sanity check",
        "Post-G33 milestones must not be review, handoff, package, bundle, launch, or human-review milestones",
        "Every new milestone must name its evidence command, expected marker, concrete thresholds, and failure boundary",
        "WT_VALIDATION_ACTIVE_TRACK_GUARDRAILS_PASS",
    ),
    "README.md": (
        "## Active terrain quality track",
        "The active direction is runtime terrain quality, not repeated human-review packaging",
        "Human-visible review remains useful as a final sanity check, but it is not the active project direction",
        "python tools/validate_active_track_guardrails.py",
        "WT_VALIDATION_ACTIVE_TRACK_GUARDRAILS_PASS",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "runtime terrain quality gates are the active direction",
        "human-visible review remains a final sanity check",
        "not the active project direction",
        "Active track guardrails",
    ),
    "docs/ROADMAP.md": (
        "## G33 - Runtime terrain quality gate",
        "this turns the active track toward terrain quality instead of review packaging",
    ),
}

ACTIVE_TITLE_TERMS = (
    "runtime",
    "terrain",
    "quality",
    "performance",
    "correctness",
    "edit",
    "latency",
    "persistence",
    "material",
    "texture",
    "storage",
    "collision",
    "streaming",
    "lod",
    "api",
)
BANNED_POST_G33_TITLE_TERMS = (
    "human",
    "review",
    "handoff",
    "bundle",
    "package",
    "packaging",
    "launch",
)


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def roadmap_milestones() -> list[tuple[int, str]]:
    text = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    milestones: list[tuple[int, str]] = []
    for line in text.splitlines():
        match = re.match(r"^## G(\d+) - (.+)$", line)
        if match:
            milestones.append((int(match.group(1)), match.group(2).strip()))
    return milestones


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing guardrail file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    post_g33_review_milestones = 0
    for number, title in roadmap_milestones():
        if number <= 33:
            continue
        lower = title.lower()
        if any(term in lower for term in BANNED_POST_G33_TITLE_TERMS):
            post_g33_review_milestones += 1
            errors.append(f"G{number} title drifts into review/packaging work: {title}")
        if not any(term in lower for term in ACTIVE_TITLE_TERMS):
            errors.append(f"G{number} title does not name terrain-quality direction: {title}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        f"{MARKER} active=runtime_terrain_quality "
        f"post_g33_review_milestones={post_g33_review_milestones}"
    )


if __name__ == "__main__":
    main()

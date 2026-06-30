#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G43_VIEW_DISTANCE_PRESENTATION_QUALITY.md",
    "tests/g43_view_distance_presentation_quality.gd",
    "tools/g43_view_distance_presentation_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G43_VIEW_DISTANCE_PRESENTATION_QUALITY.md": (
        "WT_VALIDATION_G43_CONTRACT_PASS",
        "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_PASS",
        "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS",
        "view distance presentation quality",
        "active runtime terrain quality gate",
    ),
    "tests/g43_view_distance_presentation_quality.gd": (
        "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_PASS",
        "MIN_HORIZONTAL_BINS",
        "MIN_MID_BAND_SAMPLES",
        "_capture_first_person",
        "_image_metrics",
    ),
    "tools/g43_view_distance_presentation_quality.py": (
        "WT_VALIDATION_G43_VIEW_DISTANCE_PRESENTATION_SMOKE_PASS",
        "view_distance_presentation_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G43 is the latest completed view distance presentation quality gate",
        "python tools/g43_view_distance_presentation_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G43 - View distance presentation quality",
        "view distance presentation quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G43 is the latest completed view distance presentation quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G43 - View distance presentation quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G43 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        for phrase in phrases:
            if phrase not in text and phrase not in normalized:
                errors.append(f"{relative} missing phrase: {phrase}")
    for rel in (
        "tests/g43_view_distance_presentation_quality.gd",
        "tools/g43_view_distance_presentation_quality.py",
        "tools/validate_g43_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 360:
            errors.append(f"source file exceeds G43 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G43_CONTRACT_PASS implementation=view_distance_presentation_quality")


if __name__ == "__main__":
    main()

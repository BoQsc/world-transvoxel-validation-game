#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G42_COLLISION_TRAVERSAL_STABILITY_QUALITY.md",
    "tests/g42_collision_traversal_stability_quality.gd",
    "tools/g42_collision_traversal_stability_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G42_COLLISION_TRAVERSAL_STABILITY_QUALITY.md": (
        "WT_VALIDATION_G42_CONTRACT_PASS",
        "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_PASS",
        "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS",
        "collision traversal stability quality",
        "active runtime terrain quality gate",
    ),
    "tests/g42_collision_traversal_stability_quality.gd": (
        "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_PASS",
        "MIN_FLOOR_CONTACT_RATIO",
        "MAX_OFF_FLOOR_STREAK",
        "_run_traversal_segment",
        "_submit_stability_edit",
    ),
    "tools/g42_collision_traversal_stability_quality.py": (
        "WT_VALIDATION_G42_COLLISION_TRAVERSAL_STABILITY_SMOKE_PASS",
        "collision_traversal_stability_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G42 is the latest completed collision traversal stability quality gate",
        "python tools/g42_collision_traversal_stability_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G42 - Collision traversal stability quality",
        "collision traversal stability quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G42 is the latest completed collision traversal stability quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G42 - Collision traversal stability quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G42 file: {relative}")
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
        "tests/g42_collision_traversal_stability_quality.gd",
        "tools/g42_collision_traversal_stability_quality.py",
        "tools/validate_g42_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 360:
            errors.append(f"source file exceeds G42 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G42_CONTRACT_PASS implementation=collision_traversal_stability_quality")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_FINITE_PRODUCTION_ROADMAP_PASS"

REQUIRED_PHRASES = {
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Status: active roadmap contract",
        "Completed validation track: G0 through G57",
        "automated validation-grade compact 2K terrain runtime with measured frame/update telemetry",
        "Terrain 1.0 finish line",
        "Terrain 1.0 gates",
        "Phase A - Runtime reliability and performance",
        "Phase B - Addon API and implementation boundary",
        "Phase C - Terrain generation, materials, and large-world behavior",
        "Phase D - Game-facing integration and release",
        "G41 - Runtime frame budget telemetry quality",
        "G42 - Collision traversal stability quality",
        "G43 - View distance presentation quality",
        "G44 - Edit policy and shape quality",
        "G45 - Storage recovery schema quality",
        "G46 - Terrain addon API contract quality",
        "G47 - Validation workaround removal quality",
        "G48 - Native hot-path boundary quality",
        "G49 - Debug telemetry UI quality",
        "G50 - Terrain profile standard quality",
        "G51 - Material texture pipeline quality",
        "G52 - Underground terrain variation quality",
        "G53 - Large-world streaming radius quality",
        "G54 - LOD seam and artifact quality",
        "G55 - Map generator budget quality",
        "G56 - Game-world addon prototype quality",
        "G57 - Separate game repository integration quality",
        "G58 - Documentation examples quality",
        "G59 - Versioning release contract quality",
        "G60 - Terrain 1.0 release candidate quality",
        "Post-1.0 backlog",
        "The next milestone after G57 is G58",
        "The finish line for this roadmap is G60",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "finite production roadmap",
        "G60",
        "Terrain 1.0",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "finite production roadmap",
        "G41 through G60",
        "Terrain 1.0",
    ),
    "README.md": (
        "docs/FINITE_PRODUCTION_ROADMAP.md",
        "Terrain 1.0",
        "G41 through G60",
        "G57 is the latest completed separate game repository integration quality gate",
        "python tools/g57_separate_game_repository_integration_quality.py",
        "WT_VALIDATION_G57_SEPARATE_GAME_REPOSITORY_SMOKE_PASS",
        "python tools/validate_finite_production_roadmap.py",
        "WT_VALIDATION_FINITE_PRODUCTION_ROADMAP_PASS",
    ),
}


EXPECTED_GATES = list(range(41, 61))


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def roadmap_gate_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for match in re.finditer(r"`G(\d+) - [^`]+`", text):
        number = int(match.group(1))
        if 41 <= number <= 60:
            numbers.append(number)
    return numbers


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing finite production roadmap file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")

    roadmap_path = ROOT / "docs" / "FINITE_PRODUCTION_ROADMAP.md"
    if roadmap_path.is_file():
        text = roadmap_path.read_text(encoding="utf-8")
        numbers = roadmap_gate_numbers(text)
        if numbers != EXPECTED_GATES:
            errors.append(f"finite roadmap gates must be exactly G41-G60 once each: {numbers}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(f"{MARKER} first=G41 current=G57 next=G58 final=G60 terrain_1_0=true")


if __name__ == "__main__":
    main()

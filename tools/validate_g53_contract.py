#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_G53_CONTRACT_PASS"

REQUIRED_FILES = [
    "docs/G53_LARGE_WORLD_STREAMING_RADIUS_QUALITY.md",
    "tests/g53_large_world_streaming_radius_quality.gd",
    "tools/g53_large_world_streaming_radius_quality.py",
    "tools/validate_g53_contract.py",
]

REQUIRED_PHRASES = {
    "docs/G53_LARGE_WORLD_STREAMING_RADIUS_QUALITY.md": (
        "WT_VALIDATION_G53_CONTRACT_PASS",
        "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_PASS",
        "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS",
        "radii 1, 2, 4, and 6",
        "active resource capacity 256",
    ),
    "tests/g53_large_world_streaming_radius_quality.gd": (
        "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_PASS",
        "RADIUS_STEPS",
        "ACTIVE_RESOURCE_CAPACITY := 256",
        "_verify_radius_boundary",
        "_visible_mesh_spread",
        "player_driven_viewer_enabled",
    ),
    "tools/g53_large_world_streaming_radius_quality.py": (
        "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS",
        "EXPECTED_RADII = \"1,2,4,6\"",
        "EXPECTED_RESOURCES = \"9,25,81,169\"",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G53 is a completed large-world streaming radius quality gate",
        "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G53 - Large-world streaming radius quality",
        "WT_VALIDATION_G53_LARGE_WORLD_STREAMING_RADIUS_SMOKE_PASS",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G54",
        "G53 - Large-world streaming radius quality",
    ),
    "docs/PRODUCTION_WORLD_TERRAIN_GAP_AUDIT.md": (
        "G53 locked configurable streaming radius behavior",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G53 is a completed large-world streaming radius quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G53 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing G53 phrase target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} missing phrase: {phrase}")
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if path.suffix in {".gd", ".py"} and path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G53 line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=large_world_streaming_radius_quality")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G37_STREAMING_MOVEMENT_PERFORMANCE_QUALITY.md",
    "tests/g37_streaming_movement_performance_quality.gd",
    "tools/g37_streaming_movement_performance_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G37_STREAMING_MOVEMENT_PERFORMANCE_QUALITY.md": (
        "WT_VALIDATION_G37_CONTRACT_PASS",
        "WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_PASS",
        "WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_SMOKE_PASS",
        "streaming movement performance quality",
        "active runtime terrain quality gate",
    ),
    "tests/g37_streaming_movement_performance_quality.gd": (
        "WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_PASS",
        "LOCAL_MOTION_FRAMES",
        "MAX_SETTLE_FRAMES",
        "MAX_TRANSITION_RESOURCES",
        "max_render_fading_resources",
        "_verify_route_sample",
    ),
    "tools/g37_streaming_movement_performance_quality.py": (
        "WT_VALIDATION_G37_STREAMING_MOVEMENT_PERFORMANCE_SMOKE_PASS",
        "streaming_movement_performance_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G37 is the active streaming movement performance quality gate",
        "python tools/g37_streaming_movement_performance_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G37 - Streaming movement performance quality",
        "streaming movement performance quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G37 is the active streaming movement performance quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G37 file: {relative}")
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
        "tests/g37_streaming_movement_performance_quality.gd",
        "tools/g37_streaming_movement_performance_quality.py",
        "tools/validate_g37_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 360:
            errors.append(f"source file exceeds G37 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G37_CONTRACT_PASS implementation=streaming_movement_performance_quality")


if __name__ == "__main__":
    main()

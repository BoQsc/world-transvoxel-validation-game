#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G38_STREAMING_ENDURANCE_STABILITY_QUALITY.md",
    "tests/g38_streaming_endurance_stability_quality.gd",
    "tools/g38_streaming_endurance_stability_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G38_STREAMING_ENDURANCE_STABILITY_QUALITY.md": (
        "WT_VALIDATION_G38_CONTRACT_PASS",
        "WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_PASS",
        "WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_SMOKE_PASS",
        "streaming endurance stability quality",
        "active runtime terrain quality gate",
    ),
    "tests/g38_streaming_endurance_stability_quality.gd": (
        "WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_PASS",
        "ROUTE_CYCLES",
        "MIN_TOTAL_MOTION_METERS",
        "final_cold_idle=true",
        "_run_sample",
    ),
    "tools/g38_streaming_endurance_stability_quality.py": (
        "WT_VALIDATION_G38_STREAMING_ENDURANCE_STABILITY_SMOKE_PASS",
        "streaming_endurance_stability_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G38 is the active streaming endurance stability quality gate",
        "python tools/g38_streaming_endurance_stability_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G38 - Streaming endurance stability quality",
        "streaming endurance stability quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G38 is the active streaming endurance stability quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G38 file: {relative}")
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
        "tests/g38_streaming_endurance_stability_quality.gd",
        "tools/g38_streaming_endurance_stability_quality.py",
        "tools/validate_g38_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G38 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G38_CONTRACT_PASS implementation=streaming_endurance_stability_quality")


if __name__ == "__main__":
    main()

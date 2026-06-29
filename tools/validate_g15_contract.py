#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G15_G14_SCALE_TELEMETRY.md",
    "tools/g15_g14_scale_telemetry_guard.py",
    "tools/validate_g15_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G15_G14_SCALE_TELEMETRY.md": (
        "WT_VALIDATION_G15_CONTRACT_PASS",
        "WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS",
        "4096 generated pages",
        "146400",
        "275298660",
        "137649330",
        "25 active resources",
        "vertical coverage margins",
        "two engine runtime markers",
    ),
    "tools/g15_g14_scale_telemetry_guard.py": (
        "WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS",
        "EXPECTED_DENSITY_BYTES = 275298660",
        "EXPECTED_MATERIAL_BYTES = 137649330",
        "EXPECTED_SOURCE_REVISION = 146400",
        "EXPECTED_PAGE_COUNT = 4096",
        "EXPECTED_MAX_ACTIVE_RESOURCES = 25",
        "run `python tools/g14_generated_64x64_playable_streaming_smoke.py` first",
    ),
    "README.md": (
        "python tools/validate_g15_contract.py",
        "python tools/g15_g14_scale_telemetry_guard.py",
        "WT_VALIDATION_G15_CONTRACT_PASS",
        "WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS",
        "G15 locks G14 scale telemetry",
    ),
    "docs/ROADMAP.md": (
        "## G15 - G14 scale telemetry guard",
        "WT_VALIDATION_G15_G14_SCALE_TELEMETRY_PASS",
        "275298660",
        "137649330",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G15 locks G14 scale telemetry",
        "source sizes, source revision, vertical margins, engine markers, and active-resource budget",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G15 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G15_CONTRACT_PASS implementation=g14_scale_telemetry_guard")


if __name__ == "__main__":
    main()

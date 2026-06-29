#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G13_GENERATED_FIXTURE_VERTICAL_COVERAGE.md",
    "tools/generated_fixture_vertical_coverage.py",
    "tools/g13_generated_fixture_vertical_coverage_smoke.py",
    "tools/g11_generated_16x16_playable_streaming_smoke.py",
    "tools/g12_generated_32x32_playable_streaming_smoke.py",
    "tools/validate_g13_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G13_GENERATED_FIXTURE_VERTICAL_COVERAGE.md": (
        "WT_VALIDATION_G13_CONTRACT_PASS",
        "WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS",
        "generated fixture vertical coverage guard",
        "source_revision",
        "active vertical chunk",
        "REQUIRED_UPPER_MARGIN",
    ),
    "tools/generated_fixture_vertical_coverage.py": (
        "ACTIVE_VERTICAL_MIN = 0.0",
        "ACTIVE_VERTICAL_MAX = 16.0",
        "REQUIRED_LOWER_MARGIN = 1.0",
        "REQUIRED_UPPER_MARGIN = 0.75",
        "assert_surface_within_active_vertical_chunk",
    ),
    "tools/g13_generated_fixture_vertical_coverage_smoke.py": (
        "WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS",
        "g11_vertical_coverage",
        "g12_vertical_coverage",
        "g14_vertical_coverage",
        "g13_generated_fixture_vertical_coverage_report.json",
    ),
    "tools/g11_generated_16x16_playable_streaming_smoke.py": (
        "generated_fixture_vertical_coverage",
        "vertical_coverage",
        "source revision mismatch",
        "\"vertical_coverage\"",
    ),
    "tools/g12_generated_32x32_playable_streaming_smoke.py": (
        "generated_fixture_vertical_coverage",
        "SOURCE_REVISION = 123201",
        "vertical_coverage",
        "source revision mismatch",
        "\"vertical_coverage\"",
    ),
    "README.md": (
        "python tools/validate_g13_contract.py",
        "python tools/g13_generated_fixture_vertical_coverage_smoke.py",
        "WT_VALIDATION_G13_CONTRACT_PASS",
        "WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G13 - Generated fixture vertical coverage guard",
        "WT_VALIDATION_G13_GENERATED_FIXTURE_VERTICAL_COVERAGE_PASS",
        "active vertical chunk",
        "source_revision",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G13 file: {relative}")
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
    print("WT_VALIDATION_G13_CONTRACT_PASS implementation=generated_fixture_vertical_coverage_guard")


if __name__ == "__main__":
    main()

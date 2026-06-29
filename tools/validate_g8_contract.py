#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G8_2000X2000_BOUNDED_STREAMING.md",
    "tools/g8_2000x2000_window_plan.py",
    "tools/validate_g8_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G8_2000X2000_BOUNDED_STREAMING.md": (
        "WT_VALIDATION_G8_CONTRACT_PASS",
        "WT_VALIDATION_G8_WINDOW_PLAN_PASS",
        "2000 blocks by 2000 blocks",
        "4,000,000 m²",
        "chunk size is 16 blocks",
        "125 chunks along X and 125 chunks along Z",
        "radius-2 single-viewer surface window",
        "default active chunk budget is 256 records",
        "does not claim rendered 2000×2000 terrain",
    ),
    "tools/g8_2000x2000_window_plan.py": (
        "WT_VALIDATION_G8_WINDOW_PLAN_PASS",
        "MAP_BLOCKS = 2000",
        "CHUNK_SIZE = 16",
        "CHUNK_GRID = 125",
        "ACTIVE_CHUNK_BUDGET = 256",
        "PATH_BLOCKS",
    ),
    "README.md": (
        "python tools/validate_g8_contract.py",
        "python tools/g8_2000x2000_window_plan.py",
        "WT_VALIDATION_G8_CONTRACT_PASS",
        "WT_VALIDATION_G8_WINDOW_PLAN_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G8 - 2000×2000 bounded streaming",
        "WT_VALIDATION_G8_WINDOW_PLAN_PASS",
        "2000×2000",
        "bounded active window",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G8 file: {relative}")
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
    print(
        "WT_VALIDATION_G8_CONTRACT_PASS "
        "implementation=bounded_2000x2000_streaming "
        "next=g8_runtime_active_window"
    )


if __name__ == "__main__":
    main()

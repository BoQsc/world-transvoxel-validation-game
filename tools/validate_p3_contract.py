#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
MARKER = "WT_VALIDATION_P3_CONTRACT_PASS"

REQUIRED_PHRASES = {
    "docs/P3_SCALE_COORDINATE_POLICY.md": (
        "P3-SCALE-COORDINATES",
        "large_4k_optional",
        "single_precision_no_shift",
        "65536 pages",
        "WT_VALIDATION_P3_SCALE_COORDINATE_POLICY_PASS",
    ),
    "tools/p3_scale_coordinate_policy.py": (
        "MAP_BLOCKS = 4096",
        "ACTIVE_RADIUS = 6",
        "ACTIVE_CAPACITY = 256",
        "ORIGIN_SHIFT_RESEARCH_BLOCKS = 32768",
        "WT_VALIDATION_P3_SCALE_COORDINATE_POLICY_PASS",
    ),
    "docs/POST_1_0_PRODUCTION_GAP_REGISTER.md": (
        "P3-SCALE-COORDINATES",
        "Scale and coordinate policy beyond compact 2K",
    ),
    "docs/POST_1_0_RESEARCH_AND_ROADMAP.md": (
        "P3 - Scale and coordinate policy beyond compact 2K",
        "larger-than-2K profile validates streaming",
    ),
}


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing P3 file: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not normalized_contains(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
        if path.suffix in {".py", ".gd"} and len(text.splitlines()) > 300:
            errors.append(f"P3 source file exceeds line limit: {relative}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{MARKER} implementation=scale_coordinate_policy")


if __name__ == "__main__":
    main()

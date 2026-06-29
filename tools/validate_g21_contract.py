#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G21_COMPACT_2K_HUMAN_HANDOFF.md",
    "tools/g21_compact_2k_human_handoff.py",
    "tools/validate_g21_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G21_COMPACT_2K_HUMAN_HANDOFF.md": (
        "WT_VALIDATION_G21_CONTRACT_PASS",
        "WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY",
        "g19_compact_2k_on_demand",
        "Human confirmation remains pending",
        "not a new terrain algorithm milestone",
    ),
    "tools/g21_compact_2k_human_handoff.py": (
        "WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY",
        "validate_g19_report",
        "assert_compact_project_budget",
        "pin_scene_profile",
        "human_confirmation",
        "pending",
    ),
    "README.md": (
        "G21 prepares the compact G19 project for human visual playtesting",
        "python tools/validate_g21_contract.py",
        "python tools/g21_compact_2k_human_handoff.py --import-project",
        "WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY",
    ),
    "docs/ROADMAP.md": (
        "## G21 - Compact 2K human visual handoff",
        "WT_VALIDATION_G21_COMPACT_2K_HUMAN_HANDOFF_READY",
        "human_confirmation = pending",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G21 prepares the compact G19 project for human visual playtesting",
        "human_confirmation as pending",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G21 file: {relative}")
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
    print("WT_VALIDATION_G21_CONTRACT_PASS implementation=compact_2k_human_handoff")


if __name__ == "__main__":
    main()

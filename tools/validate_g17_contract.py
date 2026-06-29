#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G17_GENERATED_128X128_HUMAN_HANDOFF.md",
    "tools/g17_generated_128x128_human_handoff.py",
    "tools/validate_g17_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G17_GENERATED_128X128_HUMAN_HANDOFF.md": (
        "WT_VALIDATION_G17_CONTRACT_PASS",
        "WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY",
        "g16_generated_128x128",
        "human visual playtesting",
        "Godot import passes",
        "human_confirmation",
    ),
    "tools/g17_generated_128x128_human_handoff.py": (
        "WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY",
        "validate_g16_runtime_report",
        "copy_fixture_into_project",
        "pin_scene_profile",
        "run_project_import",
        "human_confirmation",
    ),
    "README.md": (
        "python tools/validate_g17_contract.py",
        "python tools/g17_generated_128x128_human_handoff.py --import-project",
        "WT_VALIDATION_G17_CONTRACT_PASS",
        "WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY",
    ),
    "docs/ROADMAP.md": (
        "## G17 - Generated 128x128 human visual handoff",
        "WT_VALIDATION_G17_GENERATED_128X128_HUMAN_HANDOFF_READY",
        "stress-fixture visual confirmation is human visual playtesting",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G17 prepares the G16 near-2K generated project for human visual playtesting",
        "human_confirmation",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G17 file: {relative}")
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
    print("WT_VALIDATION_G17_CONTRACT_PASS implementation=generated_128x128_human_handoff")


if __name__ == "__main__":
    main()

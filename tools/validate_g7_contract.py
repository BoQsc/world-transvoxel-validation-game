#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G7_HUMAN_VISUAL_VERIFICATION.md",
    "tools/g7_human_visual_handoff.py",
    "tools/validate_g7_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G7_HUMAN_VISUAL_VERIFICATION.md": (
        "WT_VALIDATION_G7_CONTRACT_PASS",
        "WT_VALIDATION_G7_HANDOFF_READY",
        "flat_8x8",
        "mountain_8x8",
        "terrain is not upside down",
        "terrain does not visibly blink",
        "chunk pieces do not rapidly disappear",
        "no obvious diagonal seam",
        "2000×2000 block exploration",
    ),
    "tools/g7_human_visual_handoff.py": (
        "WT_VALIDATION_G7_HANDOFF_READY",
        "pin_scene_profile",
        "scene_is_pinned",
        "run_project_import",
        "human_confirmation",
    ),
    "README.md": (
        "python tools/validate_g7_contract.py",
        "python tools/g7_human_visual_handoff.py --reuse-bake --import-projects",
        "WT_VALIDATION_G7_CONTRACT_PASS",
        "WT_VALIDATION_G7_HANDOFF_READY",
    ),
    "docs/ROADMAP.md": (
        "## G7 - Human visual verification",
        "WT_VALIDATION_G7_HANDOFF_READY",
        "flat_8x8",
        "mountain_8x8",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G7 file: {relative}")
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
        "WT_VALIDATION_G7_CONTRACT_PASS "
        "implementation=human_visual_handoff "
        "next=human_profile_review"
    )


if __name__ == "__main__":
    main()

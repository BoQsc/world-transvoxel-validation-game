#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G40_EDIT_VISUAL_MATERIAL_FEEDBACK_QUALITY.md",
    "tests/g40_edit_visual_material_feedback_quality.gd",
    "tools/g40_edit_visual_material_feedback_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G40_EDIT_VISUAL_MATERIAL_FEEDBACK_QUALITY.md": (
        "WT_VALIDATION_G40_CONTRACT_PASS",
        "WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_PASS",
        "WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_SMOKE_PASS",
        "edit visual material feedback quality",
        "active runtime terrain quality gate",
    ),
    "tests/g40_edit_visual_material_feedback_quality.gd": (
        "WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_PASS",
        "MIN_CHANGED_SAMPLES",
        "MIN_COLORED_SAMPLES",
        "_image_difference",
        "_wait_for_material_stability",
    ),
    "tools/g40_edit_visual_material_feedback_quality.py": (
        "WT_VALIDATION_G40_EDIT_VISUAL_MATERIAL_FEEDBACK_SMOKE_PASS",
        "edit_visual_material_feedback_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G40 is the active edit visual material feedback quality gate",
        "python tools/g40_edit_visual_material_feedback_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G40 - Edit visual material feedback quality",
        "edit visual material feedback quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G40 is the active edit visual material feedback quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G40 file: {relative}")
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
        "tests/g40_edit_visual_material_feedback_quality.gd",
        "tools/g40_edit_visual_material_feedback_quality.py",
        "tools/validate_g40_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G40 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G40_CONTRACT_PASS implementation=edit_visual_material_feedback_quality")


if __name__ == "__main__":
    main()

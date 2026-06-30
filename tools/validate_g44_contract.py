#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G44_EDIT_POLICY_SHAPE_QUALITY.md",
    "tests/g44_edit_policy_shape_quality.gd",
    "tools/g44_edit_policy_shape_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G44_EDIT_POLICY_SHAPE_QUALITY.md": (
        "WT_VALIDATION_G44_CONTRACT_PASS",
        "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_PASS",
        "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS",
        "edit policy and shape quality",
        "runtime terrain quality gate",
    ),
    "scripts/validation_terrain_interactor.gd": (
        "get_edit_policy_summary",
        "alternate_shape_toggles_enabled",
        "default_brush_shape",
    ),
    "tests/g44_edit_policy_shape_quality.gd": (
        "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_PASS",
        "EXPECTED_RADIUS",
        "REPEATED_EDITS",
        "_verify_policy_summary",
        "_verify_inside_samples",
        "_verify_outside_unchanged",
    ),
    "tools/g44_edit_policy_shape_quality.py": (
        "WT_VALIDATION_G44_EDIT_POLICY_SHAPE_SMOKE_PASS",
        "edit_policy_shape_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G44 is the latest completed edit policy and shape quality gate",
        "python tools/g44_edit_policy_shape_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G44 - Edit policy and shape quality",
        "edit policy and shape quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G44 is the latest completed edit policy and shape quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G44 - Edit policy and shape quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G44 file: {relative}")
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
        "tests/g44_edit_policy_shape_quality.gd",
        "tools/g44_edit_policy_shape_quality.py",
        "tools/validate_g44_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 380:
            errors.append(f"source file exceeds G44 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G44_CONTRACT_PASS implementation=edit_policy_shape_quality")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G4_TERRAIN_EDIT_INTERACTION.md",
    "scripts/validation_terrain_interactor.gd",
    "scripts/validation_terrain_interactor.gd.uid",
    "tests/g4_edit_interaction_smoke.gd",
    "tools/g4_edit_interaction_smoke.py",
    "tools/validate_g4_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G4_TERRAIN_EDIT_INTERACTION.md": (
        "WT_VALIDATION_G4_CONTRACT_PASS",
        "WT_VALIDATION_G4_SMOKE_PASS",
        "left mouse button carves",
        "right mouse button constructs",
        "latency is measured",
        "Not claimed",
    ),
    "scenes/validation_playtest.tscn": ("ValidationTerrainInteractor",),
    "scripts/validation_terrain_interactor.gd": (
        "submit_sphere_edit",
        "MOUSE_BUTTON_LEFT",
        "MOUSE_BUTTON_RIGHT",
        "submit_edit_batch",
    ),
    "tests/g4_edit_interaction_smoke.gd": (
        "WT_VALIDATION_G4_GODOT_PASS",
        "set_human_input_enabled(false)",
        "request_authoritative_sample",
        "edit_replacements",
        "commit_frames",
        "settle_frames",
    ),
    "tools/g4_edit_interaction_smoke.py": (
        "WT_VALIDATION_G4_SMOKE_PASS",
        "g4_edit_interaction_report.json",
    ),
    "README.md": (
        "python tools/validate_g4_contract.py",
        "python tools/g4_edit_interaction_smoke.py",
        "WT_VALIDATION_G4_CONTRACT_PASS",
        "WT_VALIDATION_G4_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G4 - Terrain edit interaction",
        "Status: complete",
        "WT_VALIDATION_G4_SMOKE_PASS",
        "## G5 - Material and performance baseline",
        "Status: complete by `WT_VALIDATION_G5_CONTRACT_PASS`",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G4 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        rel = relative.as_posix()
        if ".git" in relative.parts or rel.startswith("artifacts/"):
            continue
        if path.is_file() and path.suffix in {".gd", ".py"}:
            if len(path.read_text(encoding="utf-8", errors="replace").splitlines()) > 300:
                errors.append(f"source file exceeds G4 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G4_CONTRACT_PASS "
        "implementation=first_person_edit_interaction "
        "next=g5_material_performance_baseline"
    )


if __name__ == "__main__":
    main()

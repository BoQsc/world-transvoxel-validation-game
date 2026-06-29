#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G3_TERRAIN_GENERATION_MODES.md",
    "tests/g3_generation_modes_smoke.gd",
    "tests/g3_generation_modes_smoke.gd.uid",
    "tools/g3_generation_modes_smoke.py",
    "tools/validate_g3_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G3_TERRAIN_GENERATION_MODES.md": (
        "WT_VALIDATION_G3_CONTRACT_PASS",
        "WT_VALIDATION_G3_SMOKE_PASS",
        "flat_8x8",
        "mountain_8x8",
        "8 by 8 LOD0 page set",
        "Not claimed",
    ),
    "README.md": (
        "python tools/validate_g3_contract.py",
        "python tools/g3_generation_modes_smoke.py --windowed",
        "WT_VALIDATION_G3_CONTRACT_PASS",
        "WT_VALIDATION_G3_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G3 - Terrain generation modes",
        "Status: complete",
        "WT_VALIDATION_G3_SMOKE_PASS",
        "## G4 - Terrain edit interaction",
        "WT_VALIDATION_G4_SMOKE_PASS",
    ),
    "tests/g3_generation_modes_smoke.gd": (
        "WT_VALIDATION_G3_GODOT_PASS",
        "flat_8x8",
        "mountain_8x8",
        "cold_idle",
        "render_resources",
        "collision_resources",
        "vertical_span",
    ),
    "tools/g3_generation_modes_smoke.py": (
        "WT_VALIDATION_G3_SMOKE_PASS",
        "wt_bake.py",
        "wt_storage.py",
        "chunk_pages_per_profile",
        "g3_generation_modes_report.json",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G3 file: {relative}")
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
                errors.append(f"source file exceeds G3 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G3_CONTRACT_PASS "
        "implementation=flat_and_mountain_baked_generation_modes "
        "next=g4_terrain_edit_interaction"
    )


if __name__ == "__main__":
    main()

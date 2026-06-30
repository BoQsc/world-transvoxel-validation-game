#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G27_FULL_TERRAIN_HANDOFF_PREFLIGHT.md",
    "tests/g27_full_terrain_handoff_preflight.gd",
    "tests/g27_full_terrain_handoff_preflight.gd.uid",
    "tools/g27_full_terrain_handoff_preflight.py",
    "tools/validate_g27_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G27_FULL_TERRAIN_HANDOFF_PREFLIGHT.md": (
        "WT_VALIDATION_G27_CONTRACT_PASS",
        "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS",
        "full-terrain human handoff preflight",
        "normal generated playtest scene",
        "event-driven material application",
        "bounded material-repair audit",
    ),
    "scripts/validation_terrain_materials.gd": (
        "_apply_if_signature_changed",
        "_repair_missing_materials_if_needed",
        "_runtime_signature",
        "auto_apply_count",
    ),
    "tests/g27_full_terrain_handoff_preflight.gd": (
        "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_PASS",
        "human_input_enabled = false",
        "ValidationFullTerrainVisual",
        "get_material_summary",
        "_assert_materials_stable",
        "submit_sphere_edit",
        "dense_world_files=0",
    ),
    "tools/g27_full_terrain_handoff_preflight.py": (
        "WT_VALIDATION_G27_FULL_TERRAIN_HANDOFF_PREFLIGHT_SMOKE_PASS",
        "MAX_LOAD_TO_PLAY_SECONDS = 30.0",
        "full_terrain_handoff_preflight",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G27 is the active full-terrain human handoff preflight gate",
        "python tools/validate_g27_contract.py",
        "python tools/g27_full_terrain_handoff_preflight.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G27 - Full terrain handoff preflight",
        "full-terrain human handoff preflight",
        "event-driven material application",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G27 is the active full-terrain human handoff preflight gate",
        "normal generated playtest scene",
        "event-driven material application",
        "bounded material-repair audit",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G27 file: {relative}")
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
        if path.is_file() and path.suffix in {".gd", ".py", ".gdshader"}:
            if len(path.read_text(encoding="utf-8", errors="replace").splitlines()) > 300:
                errors.append(f"source file exceeds G27 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G27_CONTRACT_PASS implementation=full_terrain_handoff_preflight")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G1_HUMAN_VISIBLE_PLAYTEST.md",
    "scripts/validation_playtest.gd",
    "tests/g1_visible_playtest_smoke.gd",
    "tools/g1_visible_playtest_smoke.py",
    "tools/validate_g1_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G1_HUMAN_VISIBLE_PLAYTEST.md": (
        "Status: active",
        "WT_VALIDATION_G1_CONTRACT_PASS",
        "WT_VALIDATION_G1_GODOT_PASS",
        "gray rectangle",
        "terrain MeshInstance3D",
    ),
    "README.md": (
        "python tools/validate_g1_contract.py",
        "python tools/g1_visible_playtest_smoke.py",
        "WT_VALIDATION_G1_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G1 - Human-visible playtest confirmation",
        "Status: active",
        "gray rectangle",
    ),
    "scripts/validation_playtest.gd": (
        "WT_VALIDATION_PLAYTEST_READY",
        "ValidationStatusOverlay",
        "ValidationMarkers",
        "look_at(viewer_position",
        "no visible terrain MeshInstance3D",
        "get_validation_summary",
    ),
    "tests/g1_visible_playtest_smoke.gd": (
        "WT_VALIDATION_G1_GODOT_PASS",
        "terrain_mesh_instances",
        "status_text",
    ),
    "tools/g1_visible_playtest_smoke.py": (
        "WT_VALIDATION_G1_SMOKE_PASS",
        "g1_visible_playtest_report.json",
        "compose(project)",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G1 file: {relative}")
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
                errors.append(f"source file exceeds G1 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print(
        "WT_VALIDATION_G1_CONTRACT_PASS "
        "implementation=human_visible_playtest_guard "
        "next=human_rerun_confirmation"
    )


if __name__ == "__main__":
    main()

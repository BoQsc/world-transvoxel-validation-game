#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "IMPLEMENTATION_CHARTER.md",
    "docs/ROADMAP.md",
    "docs/G0_INSTALL_RUN_VALIDATION.md",
    "project.godot",
    "tests/g0_install_run_smoke.gd",
    "scripts/validation_playtest.gd",
    "scenes/validation_playtest.tscn",
    "tools/compose_validation_project.py",
    "tools/g0_install_run_smoke.py",
    "tools/validate_g0_contract.py",
)

REQUIRED_PHRASES = {
    "README.md": (
        "Status: G0 install/run validation complete",
        "python tools/validate_g0_contract.py",
        "python tools/g0_install_run_smoke.py",
        "WT_VALIDATION_G0_SMOKE_PASS",
        "does not vendor addon source",
    ),
    "IMPLEMENTATION_CHARTER.md": (
        "Current phase: G0 install/run validation complete",
        "Do not copy or fork `world-transvoxel-sandbox`",
        "G0 is complete when",
        "G1 - Human-visible playtest confirmation",
    ),
    "docs/ROADMAP.md": (
        "## G0 - Install/run validation scaffold",
        "Status: complete",
        "## G1 - Human-visible playtest confirmation",
        "provide one human-visible playtest scene",
    ),
    "docs/G0_INSTALL_RUN_VALIDATION.md": (
        "Status: complete",
        "WT_VALIDATION_G0_CONTRACT_PASS",
        "WT_VALIDATION_G0_GODOT_PASS",
        "WT_VALIDATION_G0_SMOKE_PASS",
        "Godot 4.6.3 and Godot 4.7",
    ),
    "project.godot": (
        "World Transvoxel Validation Game",
        "res://scenes/validation_playtest.tscn",
    ),
    "tools/compose_validation_project.py": (
        "world-transvoxel",
        "world-transvoxel-terrain",
        "production-lifecycle-fixture",
        "VALIDATION_LOCK.json",
    ),
    "tools/g0_install_run_smoke.py": (
        "WT_VALIDATION_G0_GODOT_PASS",
        "WT_VALIDATION_G0_SMOKE_PASS",
        "compose(project)",
    ),
    "tests/g0_install_run_smoke.gd": (
        "WT_VALIDATION_G0_GODOT_PASS",
        "start_backend_world",
        "update_viewer",
        "query_chunk_state",
        "cold_idle=stable",
    ),
    "scripts/validation_playtest.gd": (
        "WT_VALIDATION_PLAYTEST_READY",
        "start_reference_backend_world",
        "update_reference_viewer",
    ),
}

FORBIDDEN_TRACKED_PATHS = (
    "addons/world_transvoxel/",
    "addons/world_transvoxel_terrain/",
    "build/production-lifecycle-fixture/",
)


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        rel = relative.as_posix()
        if ".git" in relative.parts:
            continue
        if "__pycache__" in relative.parts:
            continue
        if rel.startswith("artifacts/"):
            continue
        if path.is_file():
            files.append(relative)
    return files


def main() -> None:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G0 file: {relative}")

    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")

    for relative in iter_repo_files():
        rel = relative.as_posix()
        for forbidden in FORBIDDEN_TRACKED_PATHS:
            if rel.startswith(forbidden):
                errors.append(f"forbidden vendored path tracked in G0: {rel}")
        if relative.suffix in {".gd", ".gdshader", ".glsl", ".py"}:
            lines = (ROOT / relative).read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
            if len(lines) > 300:
                errors.append(f"source file exceeds G0 line limit: {rel}")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)

    print(
        "WT_VALIDATION_G0_CONTRACT_PASS "
        "implementation=install_run_validation_scaffold "
        "next=human_visible_playtest_confirmation"
    )


if __name__ == "__main__":
    main()

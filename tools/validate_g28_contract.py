#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G28_NORMAL_PROJECT_LAUNCH_PREFLIGHT.md",
    "tools/g28_normal_project_launch_preflight.py",
    "tools/validate_g28_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G28_NORMAL_PROJECT_LAUNCH_PREFLIGHT.md": (
        "WT_VALIDATION_G28_CONTRACT_PASS",
        "WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_PASS",
        "normal project launch preflight",
        "Godot is launched with `--path`, not `--script`",
        "automation disables human input from startup",
        "restored to human input enabled",
    ),
    "tools/g28_normal_project_launch_preflight.py": (
        "WT_VALIDATION_G28_NORMAL_PROJECT_LAUNCH_SMOKE_PASS",
        "WT_VALIDATION_PLAYTEST_READY",
        "MAX_READY_SECONDS = 30.0",
        "human_input_enabled = false",
        "--path",
        "run_normal_launch",
        "restore_human_handoff_scene",
        "handoff_human_input_restored=true",
        "normal_project_launch_preflight",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G28 is the active normal project launch preflight gate",
        "python tools/validate_g28_contract.py",
        "python tools/g28_normal_project_launch_preflight.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G28 - Normal project launch preflight",
        "normal project launch preflight",
        "Godot is launched with `--path`, not `--script`",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G28 is the active normal project launch preflight gate",
        "normal generated project launch",
        "automation disables human input",
        "restored to human input enabled",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G28 file: {relative}")
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
                errors.append(f"source file exceeds G28 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G28_CONTRACT_PASS implementation=normal_project_launch_preflight")


if __name__ == "__main__":
    main()

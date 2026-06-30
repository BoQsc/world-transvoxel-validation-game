#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G29_COMPACT_2K_HUMAN_READY_HANDOFF.md",
    "tools/g29_compact_2k_human_ready_handoff.py",
    "tools/validate_g29_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G29_COMPACT_2K_HUMAN_READY_HANDOFF.md": (
        "WT_VALIDATION_G29_CONTRACT_PASS",
        "WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS",
        "human-ready compact 2K handoff project",
        "`human_input_enabled = true`",
        "`HUMAN_REVIEW.md`",
        "G27 and G28 prerequisite reports",
    ),
    "tools/g29_compact_2k_human_ready_handoff.py": (
        "WT_VALIDATION_G29_COMPACT_2K_HUMAN_READY_HANDOFF_PASS",
        "compact_2k_human_ready_handoff",
        "HUMAN_REVIEW.md",
        "human_input_enabled",
        "assert_report_lock_matches",
        "assert_compact_project_budget",
        "run_project_import",
    ),
    "README.md": (
        "G29 is the active compact 2K human-ready handoff gate",
        "python tools/validate_g29_contract.py",
        "python tools/g29_compact_2k_human_ready_handoff.py --skip-build",
    ),
    "docs/ROADMAP.md": (
        "## G29 - Compact 2K human-ready handoff",
        "human-ready compact 2K handoff project",
        "HUMAN_REVIEW.md",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G29 is the active compact 2K human-ready handoff gate",
        "human-ready compact 2K handoff project",
        "HUMAN_REVIEW.md",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G29 file: {relative}")
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
                errors.append(f"source file exceeds G29 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G29_CONTRACT_PASS implementation=compact_2k_human_ready_handoff")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G34_EDIT_LATENCY_PERSISTENCE_QUALITY.md",
    "tests/g34_edit_latency_persistence_quality.gd",
    "tools/g34_edit_latency_persistence_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G34_EDIT_LATENCY_PERSISTENCE_QUALITY.md": (
        "WT_VALIDATION_G34_CONTRACT_PASS",
        "WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_PASS",
        "WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_SMOKE_PASS",
        "active runtime terrain quality gate",
        "edit latency and persistence",
    ),
    "tests/g34_edit_latency_persistence_quality.gd": (
        "WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_PASS",
        "MAX_COMMIT_FRAMES",
        "MAX_SETTLE_FRAMES",
        "JOURNAL_PATH",
        "_verify_replayed_sample",
    ),
    "tools/g34_edit_latency_persistence_quality.py": (
        "WT_VALIDATION_G34_EDIT_LATENCY_PERSISTENCE_SMOKE_PASS",
        "edit_latency_persistence_quality",
        "reset_compact_runtime_state",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G34 is the active edit latency and persistence quality gate",
        "python tools/g34_edit_latency_persistence_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G34 - Edit latency persistence quality",
        "edit latency and persistence",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G34 is the active edit latency and persistence quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G34 file: {relative}")
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
        "tests/g34_edit_latency_persistence_quality.gd",
        "tools/g34_edit_latency_persistence_quality.py",
        "tools/validate_g34_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G34 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G34_CONTRACT_PASS implementation=edit_latency_persistence_quality")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G39_DISTRIBUTED_EDIT_STREAMING_QUALITY.md",
    "tests/g39_distributed_edit_streaming_quality.gd",
    "tools/g39_distributed_edit_streaming_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G39_DISTRIBUTED_EDIT_STREAMING_QUALITY.md": (
        "WT_VALIDATION_G39_CONTRACT_PASS",
        "WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_PASS",
        "WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_SMOKE_PASS",
        "distributed edit streaming quality",
        "active runtime terrain quality gate",
    ),
    "tests/g39_distributed_edit_streaming_quality.gd": (
        "WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_PASS",
        "EDIT_SITES",
        "JOURNAL_PATH",
        "final_cold_idle=true",
        "_stream_edit_and_verify",
    ),
    "tools/g39_distributed_edit_streaming_quality.py": (
        "WT_VALIDATION_G39_DISTRIBUTED_EDIT_STREAMING_SMOKE_PASS",
        "distributed_edit_streaming_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G39 is the active distributed edit streaming quality gate",
        "python tools/g39_distributed_edit_streaming_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G39 - Distributed edit streaming quality",
        "distributed edit streaming quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G39 is the active distributed edit streaming quality gate",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G39 file: {relative}")
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
        "tests/g39_distributed_edit_streaming_quality.gd",
        "tools/g39_distributed_edit_streaming_quality.py",
        "tools/validate_g39_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G39 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G39_CONTRACT_PASS implementation=distributed_edit_streaming_quality")


if __name__ == "__main__":
    main()

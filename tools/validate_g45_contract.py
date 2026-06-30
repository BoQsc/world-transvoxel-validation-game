#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G45_STORAGE_RECOVERY_SCHEMA_QUALITY.md",
    "tests/g45_storage_recovery_journal.gd",
    "tests/g45_storage_recovery_compaction.gd",
    "tools/g45_storage_recovery_schema_quality.py",
]

REQUIRED_PHRASES = {
    "docs/G45_STORAGE_RECOVERY_SCHEMA_QUALITY.md": (
        "WT_VALIDATION_G45_CONTRACT_PASS",
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_PASS",
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS",
        "storage recovery schema quality",
        "truncated-tail recovery",
        "compaction/reopen",
    ),
    "scripts/validation_profile_catalog.gd": (
        "g8_sparse_2k",
        "g8_2000x2000_sparse.wtworld",
        "g19_compact_2k_on_demand",
    ),
    "tests/g45_storage_recovery_journal.gd": (
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_JOURNAL_PASS",
        "JOURNAL_PATH",
        "_append_truncated_wtedit_tail",
        "g19_compact_2k_on_demand",
    ),
    "tests/g45_storage_recovery_compaction.gd": (
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_COMPACTION_PASS",
        "OUTPUT_DIR",
        "request_world_compaction",
        "g8_sparse_2k",
    ),
    "tools/g45_storage_recovery_schema_quality.py": (
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_JOURNAL_PASS",
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_COMPACTION_PASS",
        "WT_VALIDATION_G45_STORAGE_RECOVERY_SCHEMA_SMOKE_PASS",
        "storage_recovery_schema_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G45 is the latest completed storage recovery schema quality gate",
        "python tools/g45_storage_recovery_schema_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G45 - Storage recovery schema quality",
        "Storage recovery schema quality",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G45 is the latest completed storage recovery schema quality gate",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "G45 - Storage recovery schema quality",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G45 file: {relative}")
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
        "tests/g45_storage_recovery_journal.gd",
        "tests/g45_storage_recovery_compaction.gd",
        "tools/g45_storage_recovery_schema_quality.py",
        "tools/validate_g45_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G45 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G45_CONTRACT_PASS implementation=storage_recovery_schema_quality")


if __name__ == "__main__":
    main()

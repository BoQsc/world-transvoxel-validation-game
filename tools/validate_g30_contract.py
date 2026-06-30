#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G30_COMPACT_2K_REVIEW_BUNDLE.md",
    "tools/g30_compact_2k_review_bundle.py",
    "tools/validate_g30_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G30_COMPACT_2K_REVIEW_BUNDLE.md": (
        "WT_VALIDATION_G30_CONTRACT_PASS",
        "WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS",
        "Compact 2K review bundle",
        "HANDOFF_MANIFEST.json",
        "SHA-256 hashes",
        "G27, G28, and G29 reports/logs",
    ),
    "tools/g30_compact_2k_review_bundle.py": (
        "WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS",
        "compact_2k_review_bundle",
        "HANDOFF_MANIFEST.json",
        "REVIEW_INDEX.md",
        "sha256_file",
        "evidence_sources",
        "assert_compact_project_budget",
    ),
    "README.md": (
        "G30 is the active compact 2K review bundle gate",
        "python tools/validate_g30_contract.py",
        "python tools/g30_compact_2k_review_bundle.py",
    ),
    "docs/ROADMAP.md": (
        "## G30 - Compact 2K review bundle",
        "HANDOFF_MANIFEST.json",
        "REVIEW_INDEX.md",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G30 is the active compact 2K review bundle gate",
        "Compact 2K review bundle",
        "HANDOFF_MANIFEST.json",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G30 file: {relative}")
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
                errors.append(f"source file exceeds G30 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G30_CONTRACT_PASS implementation=compact_2k_review_bundle")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G31_REVIEW_BUNDLE_LAUNCH_PREFLIGHT.md",
    "tools/g31_review_bundle_launch_preflight.py",
    "tools/validate_g31_contract.py",
)

REQUIRED_PHRASES = {
    "docs/G31_REVIEW_BUNDLE_LAUNCH_PREFLIGHT.md": (
        "WT_VALIDATION_G31_CONTRACT_PASS",
        "WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_PASS",
        "Review bundle launch preflight",
        "stale `.godot` import cache is removed",
        "source G30 bundle remains `human_input_enabled = true`",
    ),
    "tools/g31_review_bundle_launch_preflight.py": (
        "WT_VALIDATION_G31_REVIEW_BUNDLE_LAUNCH_SMOKE_PASS",
        "review_bundle_launch_preflight",
        "bundle_launch_copy",
        "human_input_enabled",
        "run_project_import",
        "READY_MARKER",
        "assert_original_bundle_human_ready",
    ),
    "README.md": (
        "G31 is the active review bundle launch preflight gate",
        "python tools/validate_g31_contract.py",
        "python tools/g31_review_bundle_launch_preflight.py",
    ),
    "docs/ROADMAP.md": (
        "## G31 - Review bundle launch preflight",
        "copied-bundle launch readiness",
        "bundle_launch_copy",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G31 is the active review bundle launch preflight gate",
        "copied-bundle launch readiness",
        "bundle_launch_copy",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G31 file: {relative}")
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
                errors.append(f"source file exceeds G31 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G31_CONTRACT_PASS implementation=review_bundle_launch_preflight")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/G32_REVIEW_BUNDLE_RUNTIME_PROOF.md",
    "tools/g32_review_bundle_runtime_proof.py",
]

REQUIRED_PHRASES = {
    "docs/G32_REVIEW_BUNDLE_RUNTIME_PROOF.md": (
        "WT_VALIDATION_G32_CONTRACT_PASS",
        "WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_PASS",
        "exact review-bundle autonomous runtime proof",
        "G25 full-terrain visual baseline",
        "G26 full-terrain playable experience",
        "G27 full-terrain handoff preflight",
        "source G30 bundle remains `human_input_enabled = true`",
    ),
    "tools/g32_review_bundle_runtime_proof.py": (
        "WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_PASS",
        "review_bundle_runtime_proof",
        "g25_full_terrain_visual_baseline",
        "g26_full_terrain_playable_experience",
        "g27_full_terrain_handoff_preflight",
        "runtime_copy_human_input=false",
        "source_bundle_human_input=true",
    ),
    "README.md": (
        "G32 is the active exact review-bundle autonomous runtime proof gate",
        "python tools/g32_review_bundle_runtime_proof.py",
        "WT_VALIDATION_G32_REVIEW_BUNDLE_RUNTIME_SMOKE_PASS",
    ),
    "docs/ROADMAP.md": (
        "## G32 - Review bundle runtime proof",
        "exact review-bundle autonomous runtime proof",
        "G25 full-terrain visual baseline",
        "G26 full-terrain playable experience",
        "G27 full-terrain handoff preflight",
    ),
    "docs/PLAYABLE_WORLD_TARGET.md": (
        "G32 is the active exact review-bundle autonomous runtime proof gate",
        "copied review-bundle runtime proof",
    ),
}


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G32 file: {relative}")
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
    for rel in ("tools/g32_review_bundle_runtime_proof.py", "tools/validate_g32_contract.py"):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G32 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G32_CONTRACT_PASS implementation=review_bundle_runtime_proof")


if __name__ == "__main__":
    main()

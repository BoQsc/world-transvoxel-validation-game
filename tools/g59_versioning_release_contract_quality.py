#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from compose_validation_project import ROOT


ARTIFACT_ROOT = ROOT / "artifacts" / "g59_versioning_release_contract_quality"
CONTRACT = ROOT / "docs" / "VERSIONING_RELEASE_CONTRACT.md"
MARKER = "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_PASS"
SUMMARY_MARKER = "WT_VALIDATION_G59_VERSIONING_RELEASE_CONTRACT_SMOKE_PASS"
SECTIONS = (
    "## Versioning",
    "## Compatibility",
    "## Migration policy",
    "## License boundary",
    "## Source/reference policy",
    "## Release checklist",
)
REQUIRED_PHRASES = (
    "semantic versioning",
    "Godot 4.6.3 stable",
    "Godot 4.7 stable",
    "Windows x86_64",
    "edit journal format",
    "MIT-licensed Transvoxel reference code",
    "0BSD replacement backend is not the default",
    "must not be claimed as an exact official replacement",
    "Do not mix original MIT source files into 0BSD implementation paths",
    "G41 through G59 validators pass",
)


def normalized_contains(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def audit_contract() -> dict[str, object]:
    if not CONTRACT.is_file():
        raise RuntimeError(f"missing contract: {CONTRACT}")
    text = CONTRACT.read_text(encoding="utf-8")
    missing = [section for section in SECTIONS if section not in text]
    missing += [phrase for phrase in REQUIRED_PHRASES if not normalized_contains(text, phrase)]
    forbidden = [phrase for phrase in ("TODO", "TBD", "exact 0BSD replacement achieved") if phrase in text]
    if missing or forbidden:
        raise RuntimeError(f"G59 release contract invalid missing={missing} forbidden={forbidden}")
    return {
        "sections": len(SECTIONS),
        "supported_godot": 2,
        "release_checklist": "## Release checklist" in text,
        "mit_boundary": normalized_contains(text, "MIT-licensed Transvoxel reference code"),
        "contract": str(CONTRACT),
    }


def main() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    audit = audit_contract()
    report_path = ARTIFACT_ROOT / "g59_versioning_release_contract_quality_report.json"
    report_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} sections={audit['sections']} supported_godot={audit['supported_godot']} "
        f"release_checklist={int(bool(audit['release_checklist']))} "
        f"mit_boundary={int(bool(audit['mit_boundary']))}"
    )
    print(
        f"{SUMMARY_MARKER} sections={audit['sections']} supported_godot={audit['supported_godot']} "
        f"release_checklist={int(bool(audit['release_checklist']))} "
        f"mit_boundary={int(bool(audit['mit_boundary']))} "
        f"report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()

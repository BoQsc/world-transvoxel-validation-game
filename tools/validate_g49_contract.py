#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/G49_DEBUG_TELEMETRY_UI_QUALITY.md",
    "scripts/validation_debug_telemetry_overlay.gd",
    "tests/g49_debug_telemetry_ui_quality.gd",
    "tools/g49_debug_telemetry_ui_quality.py",
)
REQUIRED_PHRASES = {
    "docs/G49_DEBUG_TELEMETRY_UI_QUALITY.md": (
        "WT_VALIDATION_G49_CONTRACT_PASS",
        "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_PASS",
        "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS",
        "Debug telemetry UI quality",
    ),
    "scripts/validation_debug_telemetry_overlay.gd": (
        "validation_debug_telemetry_overlay_v1",
        "active_chunks",
        "queues",
        "frame_update",
        "edit_state",
        "material_state",
        "storage_state",
        "export_debug_telemetry",
    ),
    "scenes/validation_playtest.tscn": (
        "ValidationDebugTelemetryOverlay",
        "validation_debug_telemetry_overlay.gd",
    ),
    "tests/g49_debug_telemetry_ui_quality.gd": (
        "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_PASS",
        "get_telemetry_summary",
        "export_debug_telemetry",
        "storage_visible=1",
    ),
    "tools/g49_debug_telemetry_ui_quality.py": (
        "WT_VALIDATION_G49_DEBUG_TELEMETRY_UI_SMOKE_PASS",
        "debug_telemetry_ui_quality",
        "quality_track=runtime_terrain",
    ),
    "README.md": (
        "G49 is the latest completed debug telemetry UI quality gate",
        "python tools/g49_debug_telemetry_ui_quality.py",
    ),
    "docs/ROADMAP.md": (
        "## G49 - Debug telemetry UI quality",
        "active chunks, queues, frame/update cost, edit state, material state",
    ),
    "docs/FINITE_PRODUCTION_ROADMAP.md": (
        "Completed validation track: G0 through G49",
        "The next milestone after G49 is G50",
    ),
}


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text or phrase in " ".join(text.split())


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing G49 file: {relative}")
    for relative, phrases in REQUIRED_PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing phrase input: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if not has_phrase(text, phrase):
                errors.append(f"{relative} missing phrase: {phrase}")
    overlay = ROOT / "scripts/validation_debug_telemetry_overlay.gd"
    if overlay.is_file():
        text = overlay.read_text(encoding="utf-8")
        if "get_backend_terrain" in text or "get_backend_world_state_name" in text:
            errors.append("G49 overlay uses backend internals")
    for rel in (
        "scripts/validation_debug_telemetry_overlay.gd",
        "tests/g49_debug_telemetry_ui_quality.gd",
        "tools/g49_debug_telemetry_ui_quality.py",
        "tools/validate_g49_contract.py",
    ):
        path = ROOT / rel
        if path.is_file() and len(path.read_text(encoding="utf-8").splitlines()) > 300:
            errors.append(f"source file exceeds G49 line limit: {rel}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("WT_VALIDATION_G49_CONTRACT_PASS implementation=debug_telemetry_ui_quality")


if __name__ == "__main__":
    main()

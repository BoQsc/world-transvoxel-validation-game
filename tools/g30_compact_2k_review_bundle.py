#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from compose_validation_project import ROOT
from g19_compact_2k_on_demand_smoke import PROFILE_ID, assert_compact_project_budget
from g28_normal_project_launch_preflight import MAIN_SCENE


ARTIFACT_ROOT = ROOT / "artifacts" / "g30_compact_2k_review_bundle"
G29_REPORT = (
    ROOT
    / "artifacts"
    / "g29_compact_2k_human_ready_handoff"
    / "g29_compact_2k_human_ready_handoff_report.json"
)
MARKER = "WT_VALIDATION_G30_COMPACT_2K_REVIEW_BUNDLE_PASS"


def load_report(path: Path, implementation: str) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"G30 requires report: {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("implementation") != implementation:
        raise RuntimeError(f"G30 wrong report implementation: {path}")
    if report.get("profile") != PROFILE_ID:
        raise RuntimeError(f"G30 wrong profile in report: {path}")
    return report


def reset_directory(path: Path) -> None:
    if path.exists():
        path.relative_to(ROOT)
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise RuntimeError(f"G30 missing source project: {source}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.tmp"))


def copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise RuntimeError(f"G30 missing evidence file: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, base: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def collect_files(path: Path) -> list[Path]:
    return sorted(file_path for file_path in path.rglob("*") if file_path.is_file())


def collect_budget(path: Path) -> dict[str, object]:
    files = collect_files(path)
    total = sum(file_path.stat().st_size for file_path in files)
    max_file = max(files, key=lambda item: item.stat().st_size) if files else None
    return {
        "file_count": len(files),
        "total_bytes": total,
        "max_file": max_file.relative_to(path).as_posix() if max_file else "",
        "max_file_bytes": max_file.stat().st_size if max_file else 0,
    }


def assert_project_shape(project: Path) -> None:
    project_text = (project / "project.godot").read_text(encoding="utf-8")
    scene_text = (project / "scenes" / "validation_playtest.tscn").read_text(encoding="utf-8")
    if f'run/main_scene="{MAIN_SCENE}"' not in project_text:
        raise RuntimeError("G30 bundled project does not launch validation_playtest")
    if f'playtest_profile_id = &"{PROFILE_ID}"' not in scene_text:
        raise RuntimeError("G30 bundled project is not pinned to compact profile")
    if "human_input_enabled = true" not in scene_text:
        raise RuntimeError("G30 bundled project is not human-input ready")
    if "HUMAN_REVIEW.md" not in [path.name for path in project.iterdir()]:
        raise RuntimeError("G30 bundled project is missing HUMAN_REVIEW.md")


def evidence_sources(g29_report: dict[str, object]) -> list[Path]:
    sources = [
        Path(str(g29_report["g27_report"])),
        Path(str(g29_report["g28_report"])),
        G29_REPORT,
    ]
    for report_path in list(sources):
        for log_path in sorted(report_path.parent.glob("godot-*.txt")):
            sources.append(log_path)
    return sources


def write_review_index(bundle: Path, manifest_name: str, g29_report: dict[str, object]) -> Path:
    path = bundle / "REVIEW_INDEX.md"
    lock_sources = dict(dict(g29_report["lock"])["sources"])
    path.write_text(
        "\n".join(
            [
                "# G30 compact 2K review bundle",
                "",
                "Open `project/project.godot` for human review.",
                "",
                "This bundle contains:",
                "",
                "- `project/`: human-ready generated Godot project",
                "- `project/HUMAN_REVIEW.md`: controls and review expectations",
                "- `evidence/`: prerequisite reports and Godot import/runtime logs",
                f"- `{manifest_name}`: SHA-256 hashes, source commits, and budgets",
                "",
                "Important boundary:",
                "",
                "This is a review bundle, not human approval and not final terrain art.",
                "",
                "Source commits:",
                "",
                f"- world-transvoxel: {dict(lock_sources['world-transvoxel'])['commit']}",
                f"- world-transvoxel-terrain: {dict(lock_sources['world-transvoxel-terrain'])['commit']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build compact 2K review bundle.")
    parser.add_argument("--report", type=Path, default=G29_REPORT)
    parser.add_argument("--output", type=Path, default=ARTIFACT_ROOT)
    arguments = parser.parse_args()

    g29_report = load_report(arguments.report.resolve(), "compact_2k_human_ready_handoff")
    bundle = arguments.output.resolve()
    reset_directory(bundle)
    project_source = Path(str(g29_report["project"]))
    project_target = bundle / "project"
    copy_tree(project_source, project_target)
    assert_project_shape(project_target)
    assert_compact_project_budget(project_target)
    evidence_root = bundle / "evidence"
    copied_evidence: list[Path] = []
    for source in evidence_sources(g29_report):
        target = evidence_root / source.parent.name / source.name
        copy_file(source, target)
        copied_evidence.append(target)
    index_path = write_review_index(bundle, "HANDOFF_MANIFEST.json", g29_report)
    project_budget = collect_budget(project_target)
    evidence_budget = collect_budget(evidence_root)
    manifest_path = bundle / "HANDOFF_MANIFEST.json"
    manifest = {
        "profile": PROFILE_ID,
        "main_scene": MAIN_SCENE,
        "project": "project/project.godot",
        "human_input_enabled": True,
        "source_lock": g29_report["lock"],
        "project_budget": project_budget,
        "evidence_budget": evidence_budget,
        "key_files": [
            file_record(project_target / "project.godot", bundle),
            file_record(project_target / "HUMAN_REVIEW.md", bundle),
            file_record(project_target / "scenes" / "validation_playtest.tscn", bundle),
            file_record(index_path, bundle),
        ],
        "evidence_files": [file_record(path, bundle) for path in copied_evidence],
        "implementation": "compact_2k_review_bundle",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        f"{MARKER} profile={PROFILE_ID} project=project/project.godot "
        f"manifest=HANDOFF_MANIFEST.json index=REVIEW_INDEX.md "
        f"evidence_files={len(copied_evidence)} "
        f"project_files={project_budget['file_count']} "
        f"total_bytes={project_budget['total_bytes'] + evidence_budget['total_bytes']} "
        "dense_world_files=0"
    )


if __name__ == "__main__":
    main()

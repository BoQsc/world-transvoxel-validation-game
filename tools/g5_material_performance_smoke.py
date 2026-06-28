#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import threading
import time

from compose_validation_project import ROOT, compose
from g0_install_run_smoke import discover_engines, has_godot_error, run_import


ARTIFACT_ROOT = ROOT / "artifacts" / "g5_material_performance"
G5_PROJECT = ARTIFACT_ROOT / "project"
SCRIPT = "res://tests/g5_material_performance_smoke.gd"
MARKER = "WT_VALIDATION_G5_GODOT_PASS"


def query_gpu_power() -> float | None:
    if shutil.which("nvidia-smi") is None:
        return None
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=5,
    )
    if result.returncode != 0:
        return None
    try:
        return float(result.stdout.splitlines()[0].strip())
    except (IndexError, ValueError):
        return None


def start_power_sampler(stop: threading.Event, samples: list[float]) -> threading.Thread:
    def sample() -> None:
        while not stop.is_set():
            value = query_gpu_power()
            if value is not None:
                samples.append(value)
            stop.wait(0.25)

    thread = threading.Thread(target=sample, daemon=True)
    thread.start()
    return thread


def run_smoke(project: Path, version: str, engine: Path, headless: bool) -> dict[str, object]:
    command = [str(engine)]
    if headless:
        command.append("--headless")
    command.extend(["--path", str(project), "--script", SCRIPT])
    samples: list[float] = []
    stop = threading.Event()
    sampler = start_power_sampler(stop, samples)
    result = subprocess.run(
        command,
        cwd=project,
        check=False,
        text=True,
        capture_output=True,
        errors="replace",
        timeout=180,
    )
    stop.set()
    sampler.join(timeout=2)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_ROOT / f"godot-{version}-g5.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (ARTIFACT_ROOT / f"godot-{version}-g5.stderr.txt").write_text(result.stderr, encoding="utf-8")
    combined = result.stdout + result.stderr
    print(combined, end="" if combined.endswith("\n") else "\n")
    if result.returncode != 0 or MARKER not in combined or has_godot_error(combined):
        raise RuntimeError(f"G5 material/performance smoke failed on {version}")
    capture = project / "artifacts" / "g5_material_performance" / "material_capture.png"
    if not capture.is_file():
        raise RuntimeError(f"G5 material capture missing: {capture}")
    copied_capture = ARTIFACT_ROOT / f"godot-{version}-material-capture.png"
    copied_capture.write_bytes(capture.read_bytes())
    power_avg = sum(samples) / len(samples) if samples else 0.0
    return {
        "engine": version,
        "executable": str(engine),
        "marker": next(line for line in combined.splitlines() if line.startswith(MARKER)),
        "capture": str(copied_capture),
        "gpu_power_samples": len(samples),
        "gpu_power_avg_watts": power_avg,
        "gpu_power_max_watts": max(samples) if samples else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the G5 material/performance baseline.")
    parser.add_argument("--godot", type=Path, action="append", default=[])
    parser.add_argument("--project", type=Path, default=G5_PROJECT)
    parser.add_argument("--windowed", action="store_true")
    arguments = parser.parse_args()

    project = arguments.project.resolve()
    lock = compose(project)
    engines = discover_engines(arguments.godot)
    results: list[dict[str, object]] = []
    for version, engine in engines:
        run_import(project, version, engine)
        results.append(run_smoke(project, version, engine, not arguments.windowed))
    report_path = ARTIFACT_ROOT / "g5_material_performance_report.json"
    report_path.write_text(
        json.dumps({"project": str(project), "lock": lock, "engines": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    power_samples = sum(int(result["gpu_power_samples"]) for result in results)
    power_avg = sum(float(result["gpu_power_avg_watts"]) for result in results) / max(len(results), 1)
    print(
        "WT_VALIDATION_G5_SMOKE_PASS "
        f"engines={len(results)} power_samples={power_samples} "
        f"avg_gpu_power_watts={power_avg:.2f} report={report_path.relative_to(ROOT).as_posix()}"
    )


if __name__ == "__main__":
    main()

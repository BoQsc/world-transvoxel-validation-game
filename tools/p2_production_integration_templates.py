from __future__ import annotations

from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parent / "templates" / "p2_production_integration"


def _read_template(name: str) -> str:
    return (TEMPLATE_ROOT / name).read_text(encoding="utf-8")


PROJECT_GODOT = _read_template("project.godot.txt")
MAIN_SCENE = _read_template("main.tscn.txt")
PLAYER_SCRIPT = _read_template("wt_production_player.gd.txt")
MAIN_SCRIPT = _read_template("main.gd.txt")
README = _read_template("README.md.txt")
GITIGNORE = _read_template("gitignore.txt")

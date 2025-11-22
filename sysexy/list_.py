from __future__ import annotations

from pathlib import Path
import sys

from . import app
from . vl70 import VL70

from typer import Argument, Option

ROOT = Path(__file__).parents[1] / "vl70m"


@app.command("list", help="List patches")
def list_(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
) -> None:
    for f in files or sorted(ROOT.glob("*.sysex")):
        stem = Path(f).stem
        for i, p in enumerate(VL70.read(f)):
            print(f"{stem}: {i + 1:03}: {p.name}")

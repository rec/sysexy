from __future__ import annotations

from pathlib import Path
import sys

from . import app
from . vl70 import VL70

from typer import Argument, Option

ROOT = Path(__file__).parents[1] / "vl70m"


@app.command(help="Invert patches")
def invert(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
) -> None:
    name_to_file = {}
    for f in files or sorted(ROOT.glob("*.sysex")):
        stem = Path(f).stem
        for i, p in enumerate(VL70.read(f)):
            name_to_file.setdefault(p.name, []).append(f"{stem}: {i + 1:03}")

    print(*((k, v) for k, v in name_to_file.items() if len(v) > 1), sep="\n")

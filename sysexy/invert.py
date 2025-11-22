from __future__ import annotations

from pathlib import Path
import sys

from . import app
from . import vl70

from typer import Argument, Option


@app.command(help="Invert patches")
def invert(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
) -> None:
    name_to_file = {}
    for f, patches in vl70.read(files):
        for i, p in enumerate(patches):
            name_to_file.setdefault(p.name, []).append(f"{f.stem}: {i + 1:03}")

    print(*((k, v) for k, v in name_to_file.items() if len(v) > 1), sep="\n")

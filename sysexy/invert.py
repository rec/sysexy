from __future__ import annotations

import sys
from pathlib import Path

from typer import Argument, Option

from . import app, vl70


@app.command(help="Invert patches")
def invert(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
) -> None:
    name_to_file: dict[str, list[str]] = {}
    for f, patches in vl70.read(files):
        for i, p in enumerate(patches):
            name_to_file.setdefault(p.name, []).append(f"{f.stem}: {i + 1:03}")

    print(*((k, v) for k, v in name_to_file.items() if len(v) > 1), sep="\n")

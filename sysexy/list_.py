from __future__ import annotations

import sys
from pathlib import Path

from typer import Argument, Option

from . import app, vl70


@app.command("list", help="List patches")
def list_(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
) -> None:
    for f, patches in vl70.read(files):
        for i, p in enumerate(patches):
            print(f"{f.stem}: {i + 1:03}: {p.name}")

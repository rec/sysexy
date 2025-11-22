from __future__ import annotations

from pathlib import Path
import sys

from . import app
from . import vl70

from typer import Argument, Option


@app.command("list", help="List patches")
def list_(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
) -> None:
    for f, patches in vl70.read(files):
        for i, p in enumerate(patches):
            print(f"{f.stem}: {i + 1:03}: {p.name}")

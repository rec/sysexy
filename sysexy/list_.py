from __future__ import annotations

import sys
from pathlib import Path

from typer import Argument, Option

from . import app, to_name, vl70


@app.command("list", help="List patches")
def list_(
    files: list[Path] = Argument((), help="A list of patch files"),
    root: Path | None = Option(None, "--root", "-r", help="Root directory for files"),
) -> None:
    for i, (f, patches) in enumerate(vl70.read(files, root)):
        if i:
            print()
        print(f)
        for j, p in enumerate(patches):
            print(f"{to_name(f, root)}: {j + 1:03}: {p.name}")

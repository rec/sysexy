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
    for f, patches in vl70.read(files, root):
        for i, p in enumerate(patches):
            print(f"{to_name(f, root):10}: {i + 1:03}: {p.name}")

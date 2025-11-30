from __future__ import annotations

import sys
from pathlib import Path

from typer import Argument, Option

from . import app, ROOT, vl70


@app.command("list", help="List patches")
def list_(
    files: list[Path] = Argument((), help="A list of patch files"),
    root: Path = Option(None, "--root", "-r", help="Root directory for files"),
) -> None:
    def to_name(p: Path) -> str:
        if p.is_absolute():
            if files and not root:
                return f.stem
            p = f.relative_to(root or ROOT)
        return str(p.with_suffix(""))

    for f, patches in vl70.read(files, root or ROOT):
        for i, p in enumerate(patches):
            print(f"{to_name(f):10}: {i + 1:03}: {p.name}")

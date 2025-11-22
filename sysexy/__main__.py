from __future__ import annotations

from pathlib import Path
import sys

from . vl70 import VL70


ROOT = Path(__file__).parents[1] / "vl70m"


def main(*files: str) -> None:
    # TODO: generate patch files from descriptions
    # TODO: read tag files

    for f in files or sorted(ROOT.glob("*.sysex")):
        stem = Path(f).stem
        for i, p in enumerate(VL70.read(f)):
            print(f"{stem}: {i + 1:03}: {p.name}")


if __name__ == "__main__":
    main(*sys.argv[1:])

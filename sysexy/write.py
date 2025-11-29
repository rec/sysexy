from __future__ import annotations

from functools import cached_property, partial
import contextmanager
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple
import sys

from . import app
from . import vl70

from typer import Argument, Option

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
_log = partial(print, file=sys.stderr)

"""
File format:

Name fragment
A003[-008]
"""

class Patch(NamedTuple):
    bank: str
    index: int


class WriteError(ValueError):
    pass


@app.command(help="Write patches")
def write(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
    commands: Path | None = Option(
        None, "--command-file", "-c", help="A file full of commands, or use stdin",
    ),
    output: Path = Optional(
        TIMESTAMP + ".sysex", "--output", "-o", help="Output file for sysx"
    ),
) -> None:
    banks = {f.stem: patches for f, patches in vl70.read(files)}
    patch_by_name = {p.name: p for pp in banks.values() for p in pp}
    # assert sorted(p.bank for p in patch_by_name.values()) == ["A", "B"], patch_by_name

    def patch(name: str) -> list[VL70]:
        # Match A003, b096-108, B096-b108
        if (b := name[0].upper()) in ["A", "B"]:
            bank = banks[b]
            parts = name[1:].split("-")
            if len(parts) == 1:
                parts += parts
            if len(parts) == 2:
                begin, end = parts
                if end.lower().startswith(bank):
                    end = end[1:]
                if begin.isnumeric() and end.isnumeric():
                    b, e, lb = int(begin), int(end), len(bank) - 1
                    if 0 < b < lb and 0 < e < lb:
                        return bank[b:e + 1]
                    raise WriteError(f"{name=} failed: 0 < {b}, {e} < {lb}")

        return [_get_approximate_key(patch_by_name, name)]

    patches = []
    success = True
    with command_file.open() if command_file else sys.stdin as fp:
        lines = (s for line in fp if (s := line.partition("#")[0].strip()))
        for line in lines:
            try:
                patches.extend(patch(s))
            except WriteError as e:
                _log("ERROR:", *e.args)
                success = False

    if not success:
        sys.exit(-1)

    if len(patches) > 64:
        _log(f"WARNING: number of patches truncated from {len(patches)} to 64")
        patches = patches[:64]

    with output.open("wb") as fp:
        for i, p in enumerate(patches):
            p.index = i
            fp.write(p.data)




def _patch(banks: dict[str, list[VL70]], name: str) -> list[VL70]:
    # Match A003, b096-108, B096-b108
    if (b := name[0].upper()) in ["A", "B"]:
        bank = banks[b]
        parts = name[1:].split("-")
        if len(parts) == 1:
            parts += parts
        if len(parts) == 2:
            begin, end = parts
            if end.lower().startswith(bank):
                end = end[1:]
            if begin.isnumeric() and end.isnumeric():
                b, e, lb = int(begin), int(end), len(bank) - 1
                if 0 < b < lb and 0 < e < lb:
                    return bank[b:e + 1]
                raise WriteError(f"{name=} failed: 0 < {b}, {e} < {lb}")
    return []


def _get_approximate_key(d: dict[str, list[VL70]], name: str) -> VL70:
    for rule in (
        name.__eq__,
        lambda s: s.lower() == name.lower(),
        name.startswith,
        lambda s: name.lower().startswith(s.lower()),
        name.__contains__,
        lambda s: s.lower() in name.lower(),
    ):
        if matches := [(k, v) for k, v in d.items() if rule(k)]:
            if len(matches) > 1:
                raise WriteError(f"Ambiguous {name=}: {matches=}")
            return matches[0]

    raise WriteError(f"No matches for {name=}")

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property, partial
from pathlib import Path
from typing import Any, NamedTuple, Optional

from typer import Argument, Option

from . import app, vl70
from .vl70 import VL70

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
_log = partial(print, file=sys.stderr)

"""
File format:

Name fragment
A003[-008]
"""


class WriteError(ValueError):
    pass


@app.command(help="Write patches")
def write(
    files: list[Path] = Argument(default=(), help="A list of patch files"),
    commands: Path | None = Option(
        None,
        "--command-file",
        "-c",
        help="A file full of commands, or use stdin",
    ),
    output: Path = Option(
        TIMESTAMP + ".sysex", "--output", "-o", help="Output file for sysx"
    ),
) -> None:
    with commands.open() if commands else sys.stdin as fp:
        if not (lines := [s for line in fp if (s := line.partition("#")[0].strip())]):
            sys.exit("No commands found")

    if not (source := list(vl70.read(files))):
        sys.exit("No patches found")

    banks = {f.stem: patches for f, patches in source}
    if len(banks) < len(source):
        _log(f"WARNING: {len(banks)=} < {len(source)=}:")

    expanded = [p for pp in banks.values() for p in pp]
    patch_by_name = {p.name: p for p in expanded}
    if len(patch_by_name) < len(expanded):
        _log(f"WARNING: {len(patch_by_name)=} < {len(expanded)=}:")

    patches = []
    success = True

    for line in lines:
        try:
            pp = _patch(banks, line) or [_get_approximate_key(patch_by_name, line)]
        except WriteError as e:
            _log("ERROR:", *e.args)
            success = False
        else:
            patches.extend(pp)

    if not success:
        sys.exit(-1)

    if len(patches) > 64:
        _log(f"WARNING: number of patches truncated from {len(patches)} to 64")
        patches = patches[:64]
    patch_bytes = [p.at_index(i) for i, p in enumerate(patches)]

    with output.open("wb") as fp:
        fp.writelines(patch_bytes)

    _log(f"Wrote {len(patches)} patch{'es' * (len(patches) != 1)} to {output}")


def _patch(banks: dict[str, list[VL70]], name: str) -> list[VL70]:
    # Match A003, b096-108, B096-b108
    bank_name = name[0].upper()
    if not (bank := banks.get(bank_name)):
        return []

    parts = name[1:].split("-")
    if not (0 < len(parts) <= 2):
        return []

    if len(parts) == 1:
        parts += parts

    begin, end = parts
    end = end[1:] if end.lower().startswith(bank_name) else end
    if not (begin.isnumeric() and end.isnumeric()):
        return []

    b, e, lb = int(begin), int(end), len(bank) - 1
    if not (0 < b < lb and 0 < e < lb):
        raise WriteError(f"{name=} failed: 0 < {b}, {e} < {lb}")

    # These are inclusive, closed intervals.
    return bank[b - 1 : e] if b <= e else bank[b - 1 : e - 2 : -1]


def _get_approximate_key(d: dict[str, VL70], name: str) -> VL70:
    for rule in (
        name.__eq__,
        lambda s: s.lower() == name.lower(),
        name.startswith,
        lambda s: name.lower().startswith(s.lower()),
        name.__contains__,
        lambda s: s.lower() in name.lower(),
    ):
        if matches := {k: v for k, v in d.items() if rule(k)}:
            if len(matches) > 1:
                raise WriteError(f"Ambiguous {name=}:", *matches)
            return matches.popitem()[1]

    raise WriteError(f"No matches for {name=}")

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property, partial
from pathlib import Path
from typing import Any, NamedTuple, Optional

from typer import Argument, Option

from . import app, to_name, ROOT, vl70
from .vl70 import VL70

OUTPUT = Path(datetime.now().strftime("%Y%m%d_%H%M%S.syx"))
_log = partial(print, file=sys.stderr)

"""
File format:

Name fragment
A003[-008]
"""


class WriteError(ValueError):
    pass


@dataclass
class NamedPatch:
    bank_name: str
    index: int
    patch: VL70

    def to_str(self, out_index: int | None = None):
        out = "" if out_index is None else f"{out_index + 1:03}: "
        return f"{self.bank_name}:{self.index + 1:03}  # {out}{self.patch}".strip()


@app.command(help="Write patches")
def write(
    file: str  = Argument(help="Which patch files to use"),
    commands: Path | None = Argument(None, help="A file of commands, or use stdin"),
    output: Path = Option(OUTPUT, "--output", "-o", help="Output file for sysex"),
    dry_run: bool = Option(False, "--dry-run", "-d", help="Print results, don't write")
) -> None:
    assert file in ("prog", "vl70")
    files = sorted(ROOT.glob(f"{file}/*.syx"))
    if not (source := list(vl70.read(files))):
        sys.exit("No patches found")

    banks = {f.stem: patches for f, patches in source}

    it = [NamedPatch(b, i, p) for b, v in banks.items() for i, p in enumerate(v)]
    patch_by_name = {p.patch.name: p for p in it}
    if len(patch_by_name) < len(it):
        _log(f"WARNING: {len(patch_by_name)=} < {len(it)=}:")

    patches = []
    success = True

    with commands.open() if commands else sys.stdin as fp:
        for line in fp:
            if not (lp := line.partition("#")[0].strip()):
                if commands:
                    print(line, end="")
                continue
            try:
                nps = _patch(banks, lp) or [_get_approximate_key(patch_by_name, lp)]
            except WriteError as e:
                _log("ERROR:", *e.args)
                success = False
            else:
                for named_patch in nps:
                    print(named_patch.to_str(len(patches)))
                    patches.append(named_patch.patch)

    if not success:
        sys.exit(-1)

    if len(patches) > 64:
        _log(f"WARNING: number of patches truncated from {len(patches)} to 64")
        patches = patches[:64]
    patch_bytes = [p.at_index(i) for i, p in enumerate(patches)]

    with output.open("wb") as fp:
        fp.writelines(patch_bytes)

    _log(f"Wrote {len(patches)} patch{'es' * (len(patches) != 1)} to {output}")


def _patch(banks: dict[str, list[VL70]], name: str) -> list[NamedPatch]:
    # Match A003, b096-108, B096-b108, A:003
    name = name.replace(":", "")
    bank_name = name[0].upper()
    if not (
        (bank := banks.get(bank_name))
        and (parts := name[1:].split("-"))
        and len(parts) <= 2
    ):
        return []

    begin, end = (parts + parts) if len(parts) == 1 else parts
    try:
        b, e = int(begin), int(end)
    except ValueError:
        return []

    if not (0 < b < (lb := len(bank) - 1) and 0 < e < lb):
        raise WriteError(f"{name=} failed: 0 < {b}, {e} < {lb}")

    interval = range(b - 1, e) if b <= e else range(b - 1, e - 2, -1)
    return [NamedPatch(bank_name, i, bank[i]) for i in interval]


def _get_approximate_key(d: dict[str, NamedPatch], name: str) -> NamedPatch:
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

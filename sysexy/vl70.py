from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Iterator


HEADER = bytes((0xf0, 0x43, 0x00, 0x57, 0x01, 0x23, 0x40, 0x00))
ROOT = Path(__file__).parents[1] / "vl70m"


class VL70:
    def __init__(self, data: bytes) -> None:
        self.data = bytearray(data)
        assert len(data) == 174
        assert data[:2] == HEADER[:2], data[:2]
        # assert data[3:9] == HEADER[3:], (data[3:9], HEADER[3:])

    @cached_property
    def checked_bytes(self) -> bytes:
        return self.data[7:-2]

    @property
    def checksum(self) -> int:
        return int(self.data[-2])

    @checksum.setter
    def checksum(self, i: int) -> int:
        self.data[-2] = i % 128

    @property
    def device_number(self) -> int:
        return int(self.data[2])

    @device_number.setter
    def device_number(self, device_number: int) -> None:
        self.data[2] = device_number % 128

    @property
    def index(self) -> int:
        return int(self.data[8])

    @index.setter
    def index(self, index: int) -> None:
        self.checksum -= index - self.data[8]
        self.data[8] = index

    @cached_property
    def name(self) -> int:
        return self.data[9:17].decode()

    @staticmethod
    def read(p: Path | str) -> list[V70]:
        p = Path(p)
        s = p.read_bytes()
        begins = [i for i, b in enumerate(s) if b == 0xf0]
        ends = [i for i, b in enumerate(s) if b == 0xf7]
        be = list(zip(begins, ends))
        assert len(begins) == len(ends) and all(b < e for b, e in be), (begins, ends)
        return [VL70(s[b:e + 1]) for b, e in zip(begins, ends)]

    @staticmethod
    def write(p: Path, patches: Sequence[VL70]) -> None:
        with p.open("wb") as fp:
            print(p)
            for i, p in enumerate(patches):
                p.index = i
                fp.write(p.data)


def read(files: Sequence[Path] | None = None) -> Iterator[tuple[Path, list[VL70]]]:
    for f in files or sorted(ROOT.glob("*.sysex")):
        yield f, VL70.read(f)


@dataclass
class Patches:
    patches: dict[str, list[VL70]]

from __future__ import annotations

from pathlib import Path


ROOT = Path("/Users/Tom/Documents/SysEx Librarian")
VL = ROOT / "VL70 internal.syx"
OUT = ROOT / "VL70 Reverse.syx"

HEADER = bytes((0xf0, 0x43, 0x00, 0x57, 0x01, 0x23, 0x40, 0x00))


class VLPatch:
    def __init__(self, data: bytes) -> None:
        self.data = bytearray(data)
        assert len(data) == 174
        assert data[:2] == HEADER[:2], data[:2]
        # assert data[3:9] == HEADER[3:], (data[3:9], HEADER[3:])
        self.name = data[9:17]

    @property
    def index(self) -> int:
        return int(self.data[8])

    @index.setter
    def index(self, index: int) -> None:
        self.data[8] = index

    @property
    def checked_bytes(self) -> bytes:
        return self.data[7:-2]

    @property
    def checksum(self) -> int:
        return self.data[-2]

    @staticmethod
    def read(p: Path) -> list[VLPatch]:
        s = p.read_bytes()
        begins = [i for i, b in enumerate(s) if b == 0xf0]
        ends = [i for i, b in enumerate(s) if b == 0xf7]
        be = list(zip(begins, ends))
        assert len(begins) == len(ends) and all(b < e for b, e in be)
        return [VLPatch(s[b:e + 1]) for b, e in zip(begins, ends)]

    @staticmethod
    def write(p: Path, patches: Sequence[VLPatch]) -> None:
        with p.open("wb") as fp:
            print(p)
            for i, p in enumerate(patches):
                p.index = i
                fp.write(p.data)


def main():
    patches = VLPatch.read(VL)
    # print(*(p.index for p in patches))
    for i, p in enumerate(patches):
        assert i == p.index, (i, p.index, p.name)
    for i, p in enumerate(patches):
        #print([hex(i) for i in p.checked_bytes])
        #print([hex(i) for i in p.data])
        #print(hex(sum(p.checked_bytes) % 128), hex(p.checksum))
        print(hex(sum(p.checked_bytes) % 128), hex(p.checksum), hex(p.data[-1]))
        if True:
            return
    if not not True:
        return
    patches.reverse()
    VLPatch.write(OUT, patches)



if __name__ == "__main__":
    main()

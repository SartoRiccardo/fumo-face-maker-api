from dataclasses import dataclass


@dataclass
class PECHeader:
    thumbnail_offset: int
    colors: list[int]
    width: int
    height: int

    def to_bytes(self) -> bytes:
        first_section = (
            b"LA:generated.PES   \r"
            b"            \xff\x00\x06\x26            "
            + self.color_changes.to_bytes(1, "big")
            + b"".join(clr.to_bytes(1, "big") for clr in self.colors)
        ).ljust(512)

        second_section = (
            b"\x00\x00"
            + self.thumbnail_offset.to_bytes(3, "little")
            + b"\x31\xff\xf0"
            + self.width.to_bytes(2, "little")
            + self.height.to_bytes(2, "little")
            + b"\xe0\x01\xb0\x01"
            + b"\x90\x31\x90\x00"  # 4 unknown bytes
        )

        return first_section + second_section

    @property
    def color_changes(self):
        return len(self.colors) - 1

from dataclasses import dataclass
from src.utils import sign


@dataclass
class DSTHeader:
    label: str
    stitches: int
    color_changes: int
    extend_x: tuple[int, int]
    extend_y: tuple[int, int]
    start_coords: tuple[int, int]
    multi_design_start: tuple[int, int]
    previous_design: str
    author: str | None = None
    copyright: str | None = None
    colors: list[tuple[str, str, str]] | None = None

    def to_bytes(self) -> bytes:
        def getsign(num: int) -> str:
            s = sign(num)
            return "+" if s >= 0 else "-"

        return (
            "LA:" + self.label.ljust(16) + "\r"
            "ST:" + str(self.stitches).rjust(7) + "\r"
            "CO:" + str(self.color_changes).rjust(3) + "\r"
            "+X:" + str(self.extend_x[0]).rjust(5) + "\r"
            "-X:" + str(abs(self.extend_x[1])).rjust(5) + "\r"
            "+Y:" + str(self.extend_y[0]).rjust(5) + "\r"
            "-Y:" + str(abs(self.extend_y[1])).rjust(5) + "\r"
            "AX:" + getsign(self.start_coords[0]) + str(abs(self.start_coords[0])).rjust(5) + "\r"
            "AY:" + getsign(self.start_coords[1]) + str(abs(self.start_coords[1])).rjust(5) + "\r"
            "MX:" + getsign(self.multi_design_start[0]) + str(abs(self.multi_design_start[0])).rjust(5) + "\r"
            "MY:" + getsign(self.multi_design_start[1]) + str(abs(self.multi_design_start[1])).rjust(5) + "\r"
            "PD:" + self.previous_design + "\r\x1a"
        ).ljust(512).encode()

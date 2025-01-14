# https://edutechwiki.unige.ch/en/Embroidery_format_PES
# https://edutechwiki.unige.ch/en/Embroidery_format_PEC
from .PESv1Header import PESv1Header
from .PECOpCode import PECOpCode
from .PECCommand import PECCommand
from .PECHeader import PECHeader
import math

THMB_SIZE = (0x06, 0x26)
THMB_PADDING = 2
EMPTY_THUMBNAIL = b"\x00\x00\x00\x00\x00\x00" \
                  b"\xF0\xFF\xFF\xFF\xFF\x0F" \
                  b"\x08\x00\x00\x00\x00\x10" \
                  b"\x04\x00\x00\x00\x00\x20" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x02\x00\x00\x00\x00\x40" \
                  b"\x04\x00\x00\x00\x00\x20" \
                  b"\x08\x00\x00\x00\x00\x10" \
                  b"\xF0\xFF\xFF\xFF\xFF\x0F" \
                  b"\x00\x00\x00\x00\x00\x00"

PEC_COLORS = {
    "#1a0a94": 1,
    "prussian blue": 1,
    "#0f75ff": 2,
    "blue": 2,
    "#00934c": 3,
    "teal green": 3,
    "#babdfe": 4,
    "corn flower blue": 4,
    "#ec0000": 5,
    "red": 5,
    "#e4995a": 6,
    "reddish brown": 6,
    "#cc48ab": 7,
    "magenta": 7,
    "#fdc4fa": 8,
    "light lilac": 8,
    "#dd84cd": 9,
    "lilac": 9,
    "#6bd38a": 10,
    "mint green": 10,
    "#e4a945": 11,
    "deep gold": 11,
    "#ffbd42": 12,
    "orange": 12,
    "#ffe600": 13,
    "yellow": 13,
    "#6cd900": 14,
    "lime green": 14,
    "#c1a941": 15,
    "brass": 15,
    "#b5ad97": 16,
    "silver": 16,
    "#ba9c5f": 17,
    "russet brown": 17,
    "#faf59e": 18,
    "cream brown": 18,
    "#808080": 19,
    "pewter": 19,
    "#000000": 20,
    "black": 20,
    "#001cdf": 21,
    "ultramarine": 21,
    "#df00b8": 22,
    "royal purple": 22,
    "#626262": 23,
    "dark gray": 23,
    "#69260d": 24,
    "dark brown": 24,
    "#ff0060": 25,
    "deep rose": 25,
    "#bf8200": 26,
    "light brown": 26,
    "#f39178": 27,
    "salmon pink": 27,
    "#ff6805": 28,
    "vermilion": 28,
    "#f0f0f0": 29,
    "white": 29,
    "#c832cd": 30,
    "violet": 30,
    "#b0bf9b": 31,
    "seacrest": 31,
    "#65bfeb": 32,
    "sky blue": 32,
    "#ffba04": 33,
    "pumpkin": 33,
    "#fff06c": 34,
    "cream yellow": 34,
    "#feca15": 35,
    "khaki": 35,
    "#f38101": 36,
    "clay brown": 36,
    "#37a923": 37,
    "leaf green": 37,
    "#23465f": 38,
    "peacock blue": 38,
    "#a6a695": 39,
    "gray": 39,
    "#cebfa6": 40,
    "warm gray": 40,
    "#96aa02": 41,
    "dark olive": 41,
    "#ffe3c6": 42,
    "linen": 42,
    "#ff99d7": 43,
    "pink": 43,
    "#007004": 44,
    "deep green": 44,
    "#edccfb": 45,
    "lavender": 45,
    "#c089d8": 46,
    "wisteria violet": 46,
    "#e7d9b4": 47,
    "beige": 47,
    "#e90e86": 48,
    "carmine": 48,
    "#cf6829": 49,
    "amber red": 49,
    "#408615": 50,
    "olive green": 50,
    "#db1797": 51,
    "dark fuchsia": 51,
    "#ffa704": 52,
    "tangerine": 52,
    "#b9ffff": 53,
    "light blue": 53,
    "#228927": 54,
    "emerald green": 54,
    "#b612cd": 55,
    "purple": 55,
    "#00aa00": 56,
    "moss green": 56,
    "#fea9dc": 57,
    "flesh pink": 57,
    "#fed510": 58,
    "harvest gold": 58,
    "#0097df": 59,
    "electric blue": 59,
    "#ffff84": 60,
    "lemon yellow": 60,
    "#cfe774": 61,
    "fresh green": 61,
    "#ffc864": 62,
    "applique material": 62,
    # "#ffc8c8": 63,
    "applique position": 63,
    "#ffc8c8": 64,
    "applique": 64,
}


def pes_load(fname: str) -> tuple[PESv1Header, PECHeader, list[PECCommand]]:
    with open(fname, "rb") as fin:
        pes_header_b = fin.read(PESv1Header.length())
        pes_header = PESv1Header(
            int.from_bytes(pes_header_b[8:12], "little"),
            int.from_bytes(pes_header_b[12:14], "little") != 0,
            int.from_bytes(pes_header_b[14:16], "little") != 0,
            int.from_bytes(pes_header_b[16:18], "little"),
        )

        fin.seek(pes_header.pec_section_offset)
        pec_header_b = fin.read(512 + 16)
        color_changes = pec_header_b[48]
        pec_header = PECHeader(
            int.from_bytes(pec_header_b[512+2:512+5], "little"),
            [pec_header_b[49+i] for i in range(color_changes+1)],
            int.from_bytes(pec_header_b[512+8:512+10], "little"),
            int.from_bytes(pec_header_b[512+10:512+12], "little"),
        )

        commands = []
        while (cmd := fin.read(1)) != b"\xFF":
            int_val = int.from_bytes(cmd, "big")
            cmd_len = 2
            if int_val == 0xFE:
                cmd_len = 3
            elif int_val >> 7:
                cmd_len = 4
            commands.append(PECCommand(cmd + fin.read(cmd_len-1)))
        commands.append(PECCommand(cmd))

        return pes_header, pec_header, commands


def pes_generate_header(_e) -> PESv1Header:
    return PESv1Header(
        PESv1Header.length(),
        False,
        False,
        0,
    )


def pec_generate_data(embroidery: list[PECCommand], colors: list[str | int]) -> bytes:
    min_x = min_y = float("inf")
    max_x = max_y = -float("inf")
    pos_x = pos_y = 0
    for command in embroidery:
        pos_x += command.x
        pos_y += command.y
        min_x = min(min_x, pos_x)
        max_x = max(max_x, pos_x)
        min_y = min(min_y, pos_y)
        max_y = max(max_y, pos_y)

    width, height = max_x-min_x, max_y-min_y
    """
    Without an initial JUMP command, the file is very off centered. Now, it can be
    somewhat centered if you just move it to the right by width/2 and down height/2.
    For the width (and the height too with the same principle) this works only if
        min_x = -max_x
    We are assuming min_x is always negative. Should they differ, the design will still
    be truncated by the difference in their absolute values
        truncated = max_x - |min_x|
    To correct this, subtract half of this difference to the JUMP command. The total
    amount we need to jump, therefore, becomes:
        width/2 - (max_x - |min_x|)/2
        =>  (width - (max_x + min_x)) / 2
        =>  (max_x - min_x - max_x - min_x) / 2
        =>  (-2min_x) / 2
        =>  -min_x
    """
    embroidery = [
        PECCommand(
            -min_x, -min_y,
            PECOpCode.JUMP
        ),
        *embroidery,
    ]

    stitch_data = b"".join([cmd.to_bytes() for cmd in embroidery])
    header = PECHeader(
        len(stitch_data),
        [
            clr if isinstance(clr, int) else PEC_COLORS.get(clr, PEC_COLORS["black"])
            for clr in colors
        ],
        width,
        height,
    )

    return header.to_bytes() + \
        stitch_data + \
        pec_generate_thumbnail(embroidery, (width, height))


def pec_generate_thumbnail(embroidery: list[PECCommand], size: tuple[int, int]) -> bytes:
    """Assumes min_x and min_y are both 0 (corrected with the initial JUMP)"""
    if (THMB_SIZE[0]*8-THMB_PADDING*2)/(THMB_SIZE[1]-THMB_PADDING*2) >= size[0]/size[1]:
        step = size[1]/(THMB_SIZE[1]-THMB_PADDING*2)
        padding = (int((THMB_SIZE[0]*8 - THMB_PADDING*2 - size[0] // step) // 2), 0)
    else:
        step = size[0]/(THMB_SIZE[0]*8-THMB_PADDING*2)
        print(THMB_SIZE[1] - THMB_PADDING*2, size[1])
        padding = (0, int((THMB_SIZE[1] - THMB_PADDING*2 - size[1] // step) // 2))

    thumbnail = EMPTY_THUMBNAIL
    current = EMPTY_THUMBNAIL
    x, y = 0, 0
    for cmd in embroidery:
        if cmd.op == PECOpCode.STITCH:
            if cmd.x == 0:
                angle = 90 * (-1 if cmd.y < 0 else 1)
            else:
                angle = math.atan(cmd.y / cmd.x)

            shiftx, shifty = 0, 0
            while abs(shiftx) <= abs(cmd.x) and abs(shifty) <= abs(cmd.y):
                current = mark_graphics_bit(
                    current,
                    round((x+shiftx)/step),
                    round((y+shifty)/step),
                    padding,
                )
                shiftx += math.sin(angle) * step
                shifty += math.cos(angle) * step

        if cmd.op == PECOpCode.COLOR_CHANGE or cmd.op == PECOpCode.END:
            thumbnail += current
            current = EMPTY_THUMBNAIL
        x += cmd.x
        y += cmd.y

    return thumbnail


def mark_graphics_bit(graphics: bytes, x: int, y: int, padding: tuple[int, int] = None) -> bytes:
    if padding is None:
        padding = (0, 0)
    x += THMB_PADDING + padding[0]
    y += THMB_PADDING + padding[1]
    byte = y * THMB_SIZE[0] + x // 8
    bit = x % 8
    new_byte = graphics[byte] | (1 << bit)
    return graphics[:byte] + new_byte.to_bytes(1, "big") + graphics[byte+1:]

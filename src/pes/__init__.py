# https://edutechwiki.unige.ch/en/Embroidery_format_PES
# https://edutechwiki.unige.ch/en/Embroidery_format_PEC
from .PESv1Header import PESv1Header
from .PECOpCode import PECOpCode
from .PECCommand import PECCommand
from .PECHeader import PECHeader

EMPTY_THUMBNAIL = b"\x00\x00\x00\x00\x00\x00\xF0\xFF\xFF\xFF\xFF\x0F\x08\x00\x00\x00\x00\x10\x04\x00\x00\x00\x00\x20\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x02\x00\x00\x00\x00\x40\x04\x00\x00\x00\x00\x20\x08\x00\x00\x00\x00\x10\xF0\xFF\xFF\xFF\xFF\x0F\x00\x00\x00\x00\x00\x00"
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


def pes_generate_header(_e) -> PESv1Header:
    return PESv1Header(
        PESv1Header.length(),
        False,
        False,
        0,
    )


def pec_generate_data(embroidery: list[PECCommand], colors: list[str | int]) -> bytes:
    stitch_data = b""
    for command in embroidery:
        stitch_data += command.to_bytes()

    header = PECHeader(
        len(stitch_data) + 20,
        [
            clr if isinstance(clr, int) else PEC_COLORS.get(clr, PEC_COLORS["black"])
            for clr in colors
        ],
        200,
        200,
    )

    return header.to_bytes() + stitch_data + pec_generate_thumbnail(len(colors))


def pec_generate_thumbnail(color_changes: int) -> bytes:
    return EMPTY_THUMBNAIL * (color_changes+1)

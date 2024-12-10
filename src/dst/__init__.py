# https://edutechwiki.unige.ch/en/Embroidery_format_DST
from .DSTHeader import DSTHeader
from .DSTCommand import DSTCommand
from .DSTOpCode import DSTOpCode


def dst_load(fname: str) -> tuple[DSTHeader, list[DSTCommand]]:
    with open(fname, "rb") as fin:
        header_raw = fin.read(512)
        embroidery_raw = fin.read()

    header = DSTHeader(
        header_raw[3:19].decode(),
        int(header_raw[23:30]),
        int(header_raw[34:37]),
        (int(header_raw[41:46]), int(header_raw[50:55] ) *-1),
        (int(header_raw[59:64]), int(header_raw[68:73] ) *-1),
        (int(header_raw[77:83].replace(b" ", b"")), int(header_raw[87:93].replace(b" ", b""))),
        (int(header_raw[97:103].replace(b" ", b"")), int(header_raw[107:113].replace(b" ", b""))),
        header_raw[117:123].decode(),
    )

    embroidery = [DSTCommand(embroidery_raw[i: i +3]) for i in range(0, len(embroidery_raw), 3)]

    return header, embroidery


def dst_generate_header(embroidery: list[DSTCommand]) -> DSTHeader:
    extend_x = (0, 0)
    extend_y = (0, 0)
    current_pos = [0, 0]
    color_changes = -1  # END has the same OpCode as COLOR_CHANGE but we don't wanna count it
    for cmd in embroidery:
        current_pos[0] += cmd.x
        current_pos[1] += cmd.y
        extend_x = max(extend_x[0], current_pos[0]), min(extend_x[1], current_pos[0])
        extend_y = max(extend_y[0], current_pos[1]), min(extend_y[1], current_pos[1])
        if cmd.op == DSTOpCode.COLOR_CHANGE:
            color_changes += 1

    start_pos = (abs(extend_x[1]), extend_y[0])

    return DSTHeader(
        "generated.DST",
        len(embroidery),
        color_changes,  # Color changes
        extend_x,  # X extends
        extend_y,  # Y extends
        start_pos,  # AX, AY
        (0, 0),
        "******"
    )

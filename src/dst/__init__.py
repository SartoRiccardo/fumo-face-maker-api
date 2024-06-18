# https://edutechwiki.unige.ch/en/Embroidery_format_DST
from .DSTHeader import DSTHeader
from .DSTCommand import DSTCommand
from .DSTOpCode import DSTOpCode


def dst_load(fname) -> tuple[DSTHeader, list[DSTCommand]]:
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

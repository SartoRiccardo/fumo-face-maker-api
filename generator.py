from src.dst import DSTHeader, DSTCommand, DSTOpCode


def dst_load(fname) -> tuple[DSTHeader, list[DSTCommand]]:
    with open(fname, "rb") as fin:
        header_raw = fin.read(512)
        embroidery_raw = fin.read()
    
    header = DSTHeader(
        header_raw[3:19].decode(),
        int(header_raw[23:30]),
        int(header_raw[34:37]),
        (int(header_raw[41:46]), int(header_raw[50:55])*-1),
        (int(header_raw[59:64]), int(header_raw[68:73])*-1),
        (int(header_raw[77:83].replace(b" ", b"")), int(header_raw[87:93].replace(b" ", b""))),
        (int(header_raw[97:103].replace(b" ", b"")), int(header_raw[107:113].replace(b" ", b""))),
        header_raw[117:123].decode(),
    )
    
    embroidery = [DSTCommand(embroidery_raw[i:i+3]) for i in range(0, len(embroidery_raw), 3)]
    
    return header, embroidery


def main(fname):
    header, commands = dst_load(fname)
    insert_stop_at = -1
    for i, cmd in enumerate(commands):
        if cmd.op == DSTOpCode.JUMP and insert_stop_at == -1:
            continue
        insert_stop_at = i
        if cmd.op == DSTOpCode.JUMP:
            break
        
    print(header.stitches, len(commands))
    
    header.color_changes += 1
    header.stitches += 1
    commands.insert(insert_stop_at, DSTCommand(0, 0, DSTOpCode.COLOR_CHANGE))


if __name__ == '__main__':
    main("face-parts/eyes/eye-1-lash0.DST")

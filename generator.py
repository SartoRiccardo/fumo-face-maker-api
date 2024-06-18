from src.dst import dst_load, DSTCommand, DSTOpCode


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

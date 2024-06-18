from src.dst import dst_load, DSTCommand, DSTOpCode, DSTHeader
from src.utils import get_needle_pos, sign
# 1 unit = 0.1mm


EYEBROW_CENTER = (0, 249)
MOUTH_CENTER = (0, -251)


def f1(fname):
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


def remove_last_jumps(embroidery: list[DSTCommand]) -> None:
    for i in range(len(embroidery)-1, -1, -1):
        if embroidery[i].op == DSTOpCode.JUMP:
            embroidery.pop(i)
        else:
            break


def jump_to(pos_from: tuple[int, int], pos_to: tuple[int, int]) -> list[DSTCommand]:
    movement = [pos_to[0]-pos_from[0], pos_to[1]-pos_from[1]]
    commands = []
    while sum(movement) != 0:
        move_x = min(abs(movement[0]), 121) * sign(movement[0])
        move_y = min(abs(movement[1]), 121) * sign(movement[1])
        movement[0] -= move_x
        movement[1] -= move_y
        commands.append(DSTCommand(move_x, move_y, DSTOpCode.JUMP))
    return commands


def combine_parts(
        eye_no: int,
        lash_no: int,
        brow_no: int,
        mouth_no: int,
        heterochromia: bool = False,
):
    eyeh, eyee = dst_load(f"face-parts/eyes/eye-{eye_no}-lash{lash_no}.DST")
    browh, browe = dst_load(f"face-parts/eyebrows/eyebrow-{brow_no}.DST")
    mouthh, mouthe = dst_load(f"face-parts/mouths/mouth-{mouth_no}.DST")

    embroidery_final = []

    # The very bottom of the eye must start at y=-120.
    eye_offset = -eyeh.extend_y[1] - 120  # Should never be >121
    # Don't know why there's usually 2 empty JUMPs but I'll put them out of fear.
    embroidery_final.append(DSTCommand(0, 0, DSTOpCode.JUMP))
    embroidery_final.append(DSTCommand(0, 0, DSTOpCode.JUMP))
    embroidery_final.append(DSTCommand(0, eye_offset, DSTOpCode.JUMP))

    inserted_color = -1
    for i, cmd in enumerate(eyee):
        if heterochromia and inserted_color != 1:
            if cmd.op != DSTOpCode.JUMP:
                inserted_color = 0
            elif inserted_color == 0:
                inserted_color = 1
                embroidery_final.append(DSTCommand(0, 0, DSTOpCode.COLOR_CHANGE))

        if not cmd.is_end:
            embroidery_final.append(cmd)
    remove_last_jumps(embroidery_final)

    # Eyebrows
    needle_pos = get_needle_pos(embroidery_final)
    embroidery_final += jump_to(needle_pos, EYEBROW_CENTER) + browe[:-1]
    remove_last_jumps(embroidery_final)

    # Mouth
    needle_pos = get_needle_pos(embroidery_final)
    embroidery_final += jump_to(needle_pos, MOUTH_CENTER) + mouthe

    extend_x = (0, 0)
    extend_y = (0, 0)
    current_pos = [0, 0]
    color_changes = -1  # END has the same OpCode as COLOR_CHANGE but we don't wanna count it
    for cmd in embroidery_final:
        current_pos[0] += cmd.x
        current_pos[1] += cmd.y
        extend_x = max(extend_x[0], current_pos[0]), min(extend_x[1], current_pos[0])
        extend_y = max(extend_y[0], current_pos[1]), min(extend_y[1], current_pos[1])
        if cmd.op == DSTOpCode.COLOR_CHANGE:
            color_changes += 1

    start_pos = (abs(extend_x[1]), extend_y[0])

    header = DSTHeader(
        "generated.DST",
        len(embroidery_final),
        color_changes,  # Color changes
        extend_x,  # X extends
        extend_y,  # Y extends
        start_pos,  # AX, AY
        (0, 0),
        "******"
    )

    for cmd in embroidery_final:
        print(cmd)

    content = header.to_bytes() + b"".join([cmd.to_bytes() for cmd in embroidery_final])
    with open("generated.DST", "wb") as fout:
        fout.write(content)


if __name__ == '__main__':
    #main("face-parts/eyes/eye-1-lash0.DST")
    combine_parts(1, 1, 1, 1)

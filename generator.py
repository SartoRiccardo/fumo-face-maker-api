import os
import random
import string
from src.dst import dst_load, DSTCommand, DSTOpCode, DSTHeader
from src.utils import get_needle_pos, sign
import pyembroidery
from pyembroidery.EmbThreadPec import get_thread_set
from typing import Literal
# 1 unit = 0.1mm


EYEBROW_CENTER = (0, 249)
MOUTH_CENTER = (0, -251)


def remove_last_jumps(embroidery: list[DSTCommand]) -> None:
    for i in range(len(embroidery)-1, -1, -1):
        if embroidery[i].op == DSTOpCode.JUMP:
            embroidery.pop(i)
        else:
            break


def jump_to(pos_from: tuple[int, int], pos_to: tuple[int, int]) -> list[DSTCommand]:
    movement = [pos_to[0]-pos_from[0], pos_to[1]-pos_from[1]]
    commands = []
    while any(movement):
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
        blush_no: int = 0,
        accessories: list[int] or None = None,
        heterochromia: bool = False,
        diff_clr_outline: bool = False,
        gradient: bool = False,
        eyecols: list[str] or None = None,
        outcols: list[str] or None = None,
        file_format: Literal["DST", "PES"] = "DST"
) -> bytes:
    if accessories is None:
        accessories = []
    if eyecols is None or len(eyecols) == 0:
        eyecols = ["red"]
        if heterochromia:
            eyecols.append("#0a55a3")
    if outcols is None or len(outcols) == 0:
        if diff_clr_outline:
            outcols = ["#2a1301"]
            if heterochromia:
                outcols.append("#0e1f7c")
        else:
            outcols = ["black"]

    eyeh, eyee = dst_load(f"face-parts/eyes/eye-{eye_no}-lash{lash_no}.DST")
    browh, browe = dst_load(f"face-parts/eyebrows/eyebrow-{brow_no}.DST")
    mouthh, mouthe = dst_load(f"face-parts/mouths/mouth-{mouth_no}.DST")

    embroidery_final = []
    color_change_cmd = DSTCommand(0, 0, DSTOpCode.COLOR_CHANGE)

    # The very bottom of the eye must start at y=-120.
    eye_offset = -eyeh.extend_y[1] - 120  # Should never be >121
    # Don't know why there's usually 2 empty JUMPs but I'll put them out of fear.
    embroidery_final.append(DSTCommand(0, 0, DSTOpCode.JUMP))
    embroidery_final.append(DSTCommand(0, 0, DSTOpCode.JUMP))
    embroidery_final.append(DSTCommand(0, eye_offset, DSTOpCode.JUMP))

    eye_block_count = -1
    for i, cmd in enumerate(eyee):
        if cmd.op != DSTOpCode.JUMP and i > 0 and eyee[i-1].op == DSTOpCode.JUMP:
            eye_block_count += 1
    right_eye_outl_start = 6 if eye_block_count == 10 else \
                           5 if eye_block_count == 9 else 5
    right_eye_outl_end = 8 if eye_block_count == 10 else \
                         7 if eye_block_count == 9 else 6

    current_block = -1
    for i, cmd in enumerate(eyee):
        if cmd.op != DSTOpCode.JUMP and i > 0 and eyee[i-1].op == DSTOpCode.JUMP:
            current_block += 1
            if current_block == 1 and heterochromia or \
                    current_block == right_eye_outl_end and diff_clr_outline or \
                    current_block == right_eye_outl_start and diff_clr_outline and heterochromia:
                embroidery_final.append(color_change_cmd)

        if not cmd.is_end:
            embroidery_final.append(cmd)
    remove_last_jumps(embroidery_final)

    # Eyebrows
    needle_pos = get_needle_pos(embroidery_final)
    embroidery_final += jump_to(needle_pos, EYEBROW_CENTER) + browe[:-1]
    remove_last_jumps(embroidery_final)

    # Mouth
    if mouth_no in [6, 11, 4]:  # Special mouths that don't start with black thread
        embroidery_final.append(color_change_cmd)
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

    content = header.to_bytes() + b"".join([cmd.to_bytes() for cmd in embroidery_final])

    if file_format == "PES":
        colors = [eyecols[0]]
        if heterochromia and len(eyecols) > 1:
            colors.append(eyecols[1])
        colors.append("white")
        colors.append(outcols[0])
        if diff_clr_outline:
            if heterochromia and len(outcols) > 1:
                colors.append(outcols[1])
            colors.append("black")
        # Special mouth color switches
        if mouth_no == 4:
            colors += ["white", "black"]
        elif mouth_no == 5:
            colors += ["red", "black"]
        elif mouth_no == 11:
            colors += ["white", "#fcbbc5", "black"]

        random_name = "".join(random.choices(string.ascii_letters, k=20))
    
        with open(random_name+".dst", "wb") as fout:
            fout.write(content)
        stitches = pyembroidery.read_dst(random_name+".dst")
        stitches.fix_color_count()
        for i in range(min(len(colors), len(stitches.threadlist))):
            stitches.threadlist[i].set(colors[i])
            stitches.threadlist[i].description = colors[i].capitalize()
        pyembroidery.write_pes(stitches, random_name+".pes")

        with open(random_name+".pes", "rb") as fin:
            content = fin.read()

        os.remove(random_name+".dst")
        os.remove(random_name+".pes")

    return content


if __name__ == '__main__':
    combine_parts(1, 2, 1, 11, diff_clr_outline=True, heterochromia=True)

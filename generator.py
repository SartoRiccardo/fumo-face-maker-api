#!/usr/bin/env python3
import json
import os
import random
import string
from src.dst import dst_load, dst_generate_header, DSTCommand, DSTOpCode
from src.pes import pes_generate_header
from src.utils import get_needle_pos, sign
import pyembroidery
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
        pupil_no: int = 1,
        accessories: list[int] | None = None,
        heterochromia: bool = False,
        diff_clr_outline: bool = False,
        gradient: bool = False,
        eyecols: list[str] | None = None,
        outcols: list[str] | None = None,
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

    browh, browe = dst_load(f"face-parts/eyebrows/eyebrow-{brow_no}.DST")
    mouthh, mouthe = dst_load(f"face-parts/mouths/mouth-{mouth_no}.DST")

    embroidery_final = []
    color_change_cmd = DSTCommand(0, 0, DSTOpCode.COLOR_CHANGE)

    # Don't know why there's usually 2 empty JUMPs, but I'll put them out of fear.
    embroidery_final.append(DSTCommand(0, 0, DSTOpCode.JUMP))
    embroidery_final.append(DSTCommand(0, 0, DSTOpCode.JUMP))

    # Eyes
    with open(f"face-parts/eyes/eye-{eye_no}/positions.json") as fin:
        pos_info = json.load(fin)

    eye_data = [
        (f"face-parts/eyes/eye-{eye_no}/pupils/fill-{pupil_no}-l.DST", pos_info["fill-l"][pupil_no-1], heterochromia),
        (f"face-parts/eyes/eye-{eye_no}/pupils/fill-{pupil_no}-r.DST", pos_info["fill-r"][pupil_no-1], True),
        (f"face-parts/eyes/eye-{eye_no}/shine-l.DST", pos_info["shine-l"], False),
        (f"face-parts/eyes/eye-{eye_no}/shine-r.DST", pos_info["shine-r"], True),
        (
            f"face-parts/eyes/eye-{eye_no}/outlines/eyelash-{lash_no}-l.DST",
            pos_info["outline-l"][lash_no-1],
            diff_clr_outline and heterochromia
        ),
        (
            f"face-parts/eyes/eye-{eye_no}/outlines/eyelash-{lash_no}-r.DST",
            pos_info["outline-r"][lash_no-1],
            diff_clr_outline
        ),
        (f"face-parts/eyes/eye-{eye_no}/top-l.DST", pos_info["top-l"], False),
        (f"face-parts/eyes/eye-{eye_no}/top-r.DST", pos_info["top-r"], False),
    ]

    for emb_path, abs_pos, color_change in eye_data:
        _, part = dst_load(emb_path)
        embroidery_final += jump_to(get_needle_pos(embroidery_final), tuple(abs_pos)) + part[:-1]
        if color_change:
            embroidery_final.append(color_change_cmd)
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

    header = dst_generate_header(embroidery_final)
    content = header.to_bytes() + b"".join(cmd.to_bytes() for cmd in embroidery_final)

    if file_format == "DST":
        header = dst_generate_header(embroidery_final)
        content = header.to_bytes() + b"".join(cmd.to_bytes() for cmd in embroidery_final)
    # elif file_format == "PES":
    #     header = pes_generate_header(embroidery_final)
    #     content = header.to_bytes() + b"".join(cmd.to_pec_bytes() for cmd in embroidery_final)

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
    import argparse

    parser = argparse.ArgumentParser(
        prog="generator.py",
        description="Generate Fumo faces via CLI.",
    )
    parser.add_argument("eye_no", type=int)
    parser.add_argument("lash_no", type=int)
    parser.add_argument("brow_no", type=int)
    parser.add_argument("mouth_no", type=int)
    parser.add_argument("-het", "--heterochromia", action="store_true")
    parser.add_argument("-ocol", "--outline-color", action="store_true")
    parser.add_argument("-f", "--file")

    args = parser.parse_args()

    data = combine_parts(
        args.eye_no,
        args.lash_no,
        args.brow_no,
        args.mouth_no,
        diff_clr_outline=args.outline_color,
        heterochromia=args.heterochromia,
    )

    fname = args.file if args.file else "generated.DST"
    with open(fname, "wb") as fout:
        fout.write(data)

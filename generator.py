#!/usr/bin/env python3
import json
from src.dst import dst_load, dst_generate_header, DSTCommand, DSTOpCode
from src.pes import pes_generate_header, PECCommand, PECOpCode, pec_generate_data
from src.utils import get_needle_pos, sign
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
        eye_no: int | tuple[int, int],
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
    if isinstance(eye_no, int):
        eye_no = (eye_no, eye_no)
    if accessories is None:
        accessories = []
    if eyecols is None or len(eyecols) == 0:
        eyecols = ["vermilion"]
        if heterochromia:
            eyecols.append("light blue")
    if outcols is None or len(outcols) == 0:
        if diff_clr_outline:
            outcols = ["red"]
            if heterochromia:
                outcols.append("blue")
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
    with open(f"face-parts/eyes/eye-{eye_no[0]}/positions.json") as fin:
        pos_info_0 = json.load(fin)
    if eye_no[0] == eye_no[1]:
        pos_info_1 = pos_info_0
    else:
        with open(f"face-parts/eyes/eye-{eye_no[1]}/positions.json") as fin:
            pos_info_1 = json.load(fin)

    eye_data = [
        (f"face-parts/eyes/eye-{eye_no[0]}/pupils/fill-{pupil_no}-l.DST", pos_info_0["fill-l"][pupil_no-1], heterochromia),
        (f"face-parts/eyes/eye-{eye_no[1]}/pupils/fill-{pupil_no}-r.DST", pos_info_1["fill-r"][pupil_no-1], True),
        (f"face-parts/eyes/eye-{eye_no[0]}/shine-l.DST", pos_info_0["shine-l"], False),
        (f"face-parts/eyes/eye-{eye_no[1]}/shine-r.DST", pos_info_1["shine-r"], True),
        (
            f"face-parts/eyes/eye-{eye_no[0]}/outlines/eyelash-{lash_no}-l.DST",
            pos_info_0["outline-l"][lash_no-1],
            diff_clr_outline and heterochromia
        ),
        (
            f"face-parts/eyes/eye-{eye_no[1]}/outlines/eyelash-{lash_no}-r.DST",
            pos_info_1["outline-r"][lash_no-1],
            diff_clr_outline
        ),
        (f"face-parts/eyes/eye-{eye_no[0]}/top-l.DST", pos_info_0["top-l"], False),
        (f"face-parts/eyes/eye-{eye_no[1]}/top-r.DST", pos_info_1["top-r"], False),
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

    if file_format == "DST":
        header = dst_generate_header(embroidery_final)
        return header.to_bytes() \
            + b"".join(cmd.to_bytes() for cmd in embroidery_final)
    elif file_format == "PES":
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

        color = 2
        for i, command in enumerate(embroidery_final):
            embroidery_final[i] = PECCommand.from_dst(command)
            if embroidery_final[i].op == PECOpCode.COLOR_CHANGE:
                embroidery_final[i].color = color
                color = 1 if color == 2 else 2

        return (
            pes_generate_header(embroidery_final).to_bytes()
            + pec_generate_data(embroidery_final, colors)
        )


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
    parser.add_argument("-fmt", "--format")
    parser.add_argument("-e2", "--eye2", type=int)

    args = parser.parse_args()

    format = args.format.upper() if args.format else "DST"
    eye_no = args.eye_no if args.eye2 is None else (args.eye_no, args.eye2)
    data = combine_parts(
        eye_no,
        args.lash_no,
        args.brow_no,
        args.mouth_no,
        diff_clr_outline=args.outline_color,
        heterochromia=args.heterochromia,
        file_format=format,
    )

    fname = args.file if args.file else f"generated.{format}"
    with open(fname, "wb") as fout:
        fout.write(data)

#!/usr/bin/env python3
import json
from src.embroidery.dst import dst_load, dst_generate_header, DSTCommand, DSTOpCode
from src.embroidery.pes import pes_generate_header, PECCommand, PECOpCode, pec_generate_data
from src.embroidery.utils import sign
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


def sum_tuples(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return a[0]+b[0], a[1]+b[1]


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


def optimize_jumps(embroidery: list[DSTCommand]) -> None:
    """Optimizes JUMP commands in-place"""
    i = 0
    jump = (0, 0)
    while i < len(embroidery):
        if embroidery[i].op == DSTOpCode.JUMP:
            cmd = embroidery.pop(i)
            jump = sum_tuples(jump, (cmd.x, cmd.y))
        else:
            if jump != (0, 0):
                added_cmds = jump_to((0, 0), jump)
                for cmd in added_cmds:
                    embroidery.insert(i, cmd)
                i += len(added_cmds)
                jump = (0, 0)
            i += 1


def append_commands(
        append_to: list[DSTCommand],
        *embroideries: list[DSTCommand],
        current_position: tuple[int, int] = None,
) -> tuple[int, int]:
    """
    Appends to_append embroidery_final.
    :param append_to: The array to append to
    :param embroideries: The commands to append
    :param current_position: The current needle position
    :return: The new needle position
    """
    if current_position is None:
        current_position = (0, 0)
    for commands in embroideries:
        for cmd in commands:
            current_position = sum_tuples(current_position, (cmd.x, cmd.y))
            append_to.append(cmd)
    return current_position


def combine_parts(
        eye_no: int | tuple[int, int],
        lash_no: int,
        brow_no: int,
        mouth_no: int,
        blush_no: int = 0,
        fill_no: int = 1,
        accessories: list[int] | None = None,
        heterochromia: bool = False,
        diff_clr_outline: bool = False,
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
        if fill_no != 1:
            eyecols.append("salmon pink")
            if heterochromia:
                eyecols.append("#c089d8")
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
    cur_needle_pos = (0, 0)

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

    _, fill_l = dst_load(f"face-parts/eyes/eye-{eye_no[0]}/pupils/fill-{fill_no}-l.DST")
    _, fill_r = dst_load(f"face-parts/eyes/eye-{eye_no[1]}/pupils/fill-{fill_no}-r.DST")
    fills = [fill_l, fill_r]
    fills_idx = [0, 0]
    fills_pos = [pos_info_0["fill-l"][fill_no-1], pos_info_1["fill-r"][fill_no-1]]
    idx_copy = 0

    cur_needle_pos = append_commands(
        embroidery_final,
        jump_to(cur_needle_pos, fills_pos[0]),
        current_position=cur_needle_pos,
    )
    while fills_idx[0] < len(fills[0]) or fills_idx[1] < len(fills[1]):
        prev_idx = idx_copy
        append_clr = False
        command = fills[idx_copy][fills_idx[idx_copy]]
        if command.op == DSTOpCode.COLOR_CHANGE or command.is_end:
            fills_idx[idx_copy] += 1
            if heterochromia:
                append_clr = True
            idx_copy = (idx_copy + 1) % len(fills)

            cur_needle_pos = append_commands(
                embroidery_final,
                jump_to(fills_pos[prev_idx], fills_pos[idx_copy]),
                current_position=cur_needle_pos,
            )
        else:
            embroidery_final.append(command)
            cur_needle_pos = sum_tuples(cur_needle_pos, (command.x, command.y))
            fills_pos[idx_copy] = sum_tuples(fills_pos[idx_copy], (command.x, command.y))
            fills_idx[idx_copy] += 1

        if idx_copy == 0 and idx_copy != prev_idx:
            append_clr = True
        if append_clr:
            embroidery_final.append(DSTCommand.color_change())

    eye_data = [
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
        cur_needle_pos = append_commands(
            embroidery_final,
            jump_to(cur_needle_pos, abs_pos),
            part[:-1],
            current_position=cur_needle_pos,
        )
        if color_change:
            embroidery_final.append(DSTCommand.color_change())

    # Eyebrows
    cur_needle_pos = append_commands(
        embroidery_final,
        jump_to(cur_needle_pos, EYEBROW_CENTER),
        browe[:-1],
        current_position=cur_needle_pos,
    )

    # Mouth
    if mouth_no in [6, 11, 4]:  # Special mouths that don't start with black thread
        embroidery_final.append(DSTCommand.color_change())
    cur_needle_pos = append_commands(
        embroidery_final,
        jump_to(cur_needle_pos, MOUTH_CENTER),
        mouthe,
        current_position=cur_needle_pos,
    )

    # Cleanup
    optimize_jumps(embroidery_final)

    if file_format == "DST":
        header = dst_generate_header(embroidery_final)
        return header.to_bytes() \
            + b"".join(cmd.to_bytes() for cmd in embroidery_final)
    elif file_format == "PES":
        colors = [eyecols[0]]
        if heterochromia and len(eyecols) > 1:
            colors.append(eyecols[min(1, len(eyecols)-1)])
        if fill_no != 1:
            colors.append(eyecols[min(2, len(eyecols)-1)])
            if heterochromia:
                colors.append(eyecols[min(3, len(eyecols)-1)])
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
    parser.add_argument("eye_no", type=int, help="The number of the eyes")
    parser.add_argument("lash_no", type=int, help="The number of the eyelashes")
    parser.add_argument("brow_no", type=int, help="The number of the eyebrows")
    parser.add_argument("mouth_no", type=int, help="The number of the mouth")
    parser.add_argument("-het", "--heterochromia", action="store_true", help="Makes eyes a different thread color")
    parser.add_argument("-ocol", "--outline-color", action="store_true",
                        help="Makes the eye outlines a different color from black.\n"
                             "If -het is enabled, both outlines will have a different color.")
    parser.add_argument("-f", "--file", help="The name of the file to output it to")
    parser.add_argument("-fmt", "--format", help="The format of the file to output it to")
    parser.add_argument("-e2", "--eye2", type=int, help="The number of the right eye (defaults to eye_no).")
    parser.add_argument(
        "--fill",
        type=int,
        help="The number of the eye filling. Defaults to mono color.",
        default=1
    )

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
        fill_no=args.fill,
    )

    fname = args.file if args.file else f"generated.{format}"
    with open(fname, "wb") as fout:
        fout.write(data)

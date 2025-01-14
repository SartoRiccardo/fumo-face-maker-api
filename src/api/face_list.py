import os
import json
from aiohttp import web
from src.embroidery.dst import dst_load, DSTOpCode
from generator import MOUTH_CENTER, EYEBROW_CENTER


def stitches_to_points(path: str, start_pos: tuple[int, int]) -> list[str]:
    pos_x, pos_y = start_pos
    pos_y *= -1
    _, commands = dst_load(path)
    paths = []
    current = None
    for i, c in enumerate(commands):
        pos_x += c.x
        pos_y -= c.y
        if c.op == DSTOpCode.STITCH and (c.x != 0 or c.y != 0):
            if current is None:
                current = f"m{pos_x}{' ' if pos_y >= 0 else ''}{pos_y}"
            current += f"{' ' if c.x >= 0 else ''}{c.x}{' ' if -c.y >= 0 else ''}{-c.y}"
        elif current is not None and (
                c.op == DSTOpCode.COLOR_CHANGE or
                c.is_end or
                c.op == DSTOpCode.JUMP and commands[i-1].op == DSTOpCode.STITCH
        ):
            paths.append(current)
            current = None
    return paths


async def get(_r: web.Request) -> web.Response:
    """
    Right now returns polyline data but path seems shorter
    """
    count = {
        "eyes": 0,
        "eyelashes": 0,
        "fills": 0,
        "eyebrows": 0,
        "mouths": 0,
    }
    svg_paths = {
        "mouths": [],
        "eyebrows": [],
        "eyes": [],
    }

    for fname in os.listdir("face-parts/mouths"):
        if not fname.startswith("mouth-"):
            continue
        count["mouths"] += 1
        svg_paths["mouths"].append({
            "id": int(fname[len("mouth-"):-len(".DST")]),
            "paths": stitches_to_points(f"face-parts/mouths/{fname}", MOUTH_CENTER),
        })

    for fname in os.listdir("face-parts/eyebrows"):
        if not fname.startswith("eyebrow-"):
            continue
        count["eyebrows"] += 1
        svg_paths["eyebrows"].append({
            "id": int(fname[len("eyebrow-"):-len(".DST")]),
            "paths": stitches_to_points(f"face-parts/eyebrows/{fname}", EYEBROW_CENTER),
        })

    for dname_eye in os.listdir("face-parts/eyes"):
        if not dname_eye.startswith("eye-"):
            continue
        count["eyes"] += 1

        with open(f"face-parts/eyes/{dname_eye}/positions.json") as fin:
            positions = json.load(fin)
        eye_svg_data = {
            "id": int(dname_eye[len("eye-"):]),
            "left": {
                "eyelashes": [],
                "pupils": [],
                "shine": stitches_to_points(f"face-parts/eyes/{dname_eye}/shine-l.DST", positions["shine-l"])[0],
                "top": stitches_to_points(f"face-parts/eyes/{dname_eye}/top-l.DST", positions["top-l"])[0],
            },
            "right": {
                "eyelashes": [],
                "pupils": [],
                "shine": stitches_to_points(f"face-parts/eyes/{dname_eye}/shine-r.DST", positions["shine-r"])[0],
                "top": stitches_to_points(f"face-parts/eyes/{dname_eye}/top-r.DST", positions["top-r"])[0],
            },
        }

        for fname in os.listdir(f"face-parts/eyes/{dname_eye}/outlines"):
            if dname_eye == "eye-1" and fname.startswith("eyelash-") and fname.endswith("-r.DST"):
                count["fills"] += 1
            if fname.endswith("-r.DST"):
                lash_id = int(fname[len("eyelash-"):-len("-r.DST")])
                eye_svg_data["right"]["eyelashes"].append({
                    "id": lash_id,
                    "paths": stitches_to_points(
                        f"face-parts/eyes/{dname_eye}/outlines/{fname}",
                        positions["outline-r"][lash_id-1],
                    ),
                })
                eye_svg_data["left"]["eyelashes"].append({
                    "id": lash_id,
                    "paths": stitches_to_points(
                        f"face-parts/eyes/{dname_eye}/outlines/{fname.replace('-r', '-l')}",
                        positions["outline-l"][lash_id-1],
                    ),
                })

        for fname in os.listdir(f"face-parts/eyes/{dname_eye}/pupils"):
            if dname_eye == "eye-1" and fname.startswith("fill-") and fname.endswith("-r.DST"):
                count["fills"] += 1
            if fname.endswith("-r.DST"):
                fill_id = int(fname[len("fill-"):-len("-r.DST")])
                eye_svg_data["right"]["pupils"].append({
                    "id": fill_id,
                    "paths": stitches_to_points(
                        f"face-parts/eyes/{dname_eye}/pupils/{fname}",
                        positions["fill-r"][fill_id-1],
                    ),
                })
                eye_svg_data["left"]["pupils"].append({
                    "id": fill_id,
                    "paths": stitches_to_points(
                        f"face-parts/eyes/{dname_eye}/pupils/{fname.replace('-r', '-l')}",
                        positions["fill-l"][fill_id-1],
                    ),
                })

        svg_paths["eyes"].append(eye_svg_data)

    parts = {
        "count": count,
        "svg_paths": svg_paths
    }

    return web.json_response(parts)

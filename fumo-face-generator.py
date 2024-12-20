import os
from config import Hosting
from aiohttp import web
import generator


async def list_parts(_r: web.Request) -> web.Response:
    parts = {
        "eyes": len([f for f in os.listdir("face-parts/eyes") if f.startswith("eye-")]),
        "eyelashes": len([
            f for f in os.listdir("face-parts/eyes/eye-1/outlines")
            if f.startswith("eyelash-") and f.endswith("-r.DST")
        ]),
        "fills": len([
            f for f in os.listdir("face-parts/eyes/eye-1/pupils")
            if f.startswith("fill-") and f.endswith("-r.DST")
        ]),
        "eyebrows": len([f for f in os.listdir("face-parts/eyebrows") if f.startswith("eyebrow-")]),
        "mouths": len([f for f in os.listdir("face-parts/mouths") if f.startswith("mouth-")]),
    }
    return web.json_response(parts)


async def make_face(request: web.Request) -> web.Response:
    try:
        eye_no = int(request.query["eyes"])
        lash_no = int(request.query["eyelashes"])
        brow_no = int(request.query["eyebrows"])
        mouth_no = int(request.query["mouth"])
        eyecols = request.query["eyecols"].split(",")[:2] if "eyecols" in request.query else None
        outcols = request.query["outcols"].split(",")[:2] if "outcols" in request.query else None
        heterochromia = request.query.get("heterochromia", "false").lower() != "false"
        diff_clr_outline = request.query.get("diff_clr_outline", "false").lower() != "false"
        file_format = request.query.get("format", "DST").upper()
        fill_no = int(request.query.get("fill_no", "1"))
        eye2_no = int(request.query.get("eye2_no", str(eye_no)))
    except KeyError as keyerr:
        return web.Response(status=400, text=f"Missing {keyerr}")
    except ValueError as verr:
        return web.Response(status=400, text=f"Invalid value: {verr}")

    filename = f"generated-e{eye_no}+{eye2_no}l{lash_no}b{brow_no}m{mouth_no}f{fill_no}"
    fname_attrs = "".join([
        "H" if heterochromia else "",
        "Dco" if diff_clr_outline else "",
    ])
    if len(fname_attrs) > 0:
        filename += f"-{fname_attrs}"
    filename += f".{file_format}"

    try:
        face = generator.combine_parts(
            (eye_no, eye2_no),
            lash_no,
            brow_no,
            mouth_no,
            heterochromia=heterochromia,
            diff_clr_outline=diff_clr_outline,
            eyecols=eyecols,
            outcols=outcols,
            file_format=file_format,
            fill_no=fill_no,
        )  # TODO dont block
    except FileNotFoundError as fnferr:
        return web.Response(status=400, text=f"Part not found: {fnferr.filename}")

    return web.Response(body=face, headers={"Content-Disposition": f"inline; filename=\"{filename}\""})


def main():
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    app = web.Application()
    app.add_routes([
        web.get("/face/list", list_parts),
        web.get("/face", make_face),
    ])

    web.run_app(app, host=Hosting.host, port=Hosting.port)


if __name__ == '__main__':
    main()

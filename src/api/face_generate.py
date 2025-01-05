from aiohttp import web
import generator


async def get(request: web.Request) -> web.Response:
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

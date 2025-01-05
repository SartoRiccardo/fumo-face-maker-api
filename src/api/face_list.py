import os
from aiohttp import web


async def get(_r: web.Request) -> web.Response:
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

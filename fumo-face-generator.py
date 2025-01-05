import os
from config import Hosting
from aiohttp import web
import src.api.face_generate
import src.api.face_list


def main():
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    app = web.Application()
    app.add_routes([
        web.get("/face/list", src.api.face_list.get),
        web.get("/face", src.api.face_generate.get),
    ])

    web.run_app(app, host=Hosting.host, port=Hosting.port)


if __name__ == '__main__':
    main()

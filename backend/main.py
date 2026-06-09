from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes.upload_routes import router
from backend.socket_server import sio

import socketio


app = FastAPI()

# REST routes
app.include_router(router)


# Serve frontend assets
app.mount(
    "/css",
    StaticFiles(directory="frontend/css"),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory="frontend/js"),
    name="js"
)


@app.get("/")
async def home():
    return FileResponse(
        Path("frontend/index.html")
    )


# Socket.IO ASGI app
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app
)
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.socket_server import sio

import socketio

app = FastAPI()


# ----------------------------------------------------
# Upload directory
# ----------------------------------------------------
UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ----------------------------------------------------
# File upload endpoint
# ----------------------------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    path = UPLOAD_DIR / file.filename

    with open(path, "wb") as f:
        f.write(contents)

    return {"status": "success", "file": file.filename}


# ----------------------------------------------------
# Static frontend assets
# ----------------------------------------------------
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")

app.mount("/js", StaticFiles(directory="frontend/js"), name="js")


# ----------------------------------------------------
# Homepage
# ----------------------------------------------------
@app.get("/")
async def home():
    return FileResponse(Path("frontend/index.html"))


# ----------------------------------------------------
# Socket.IO ASGI application
# ----------------------------------------------------
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

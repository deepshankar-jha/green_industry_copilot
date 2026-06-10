from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Form
import asyncio

import json
from pathlib import Path
from process_extractor import ProcessExtractor
from socket_server import sio

import socketio

extractor = ProcessExtractor()
app = FastAPI()

# ----------------------------------------------------
# Upload directory
# ----------------------------------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ----------------------------------------------------
# File upload endpoint
# ----------------------------------------------------
@app.post("/mock-upload")
async def mock_upload(file: UploadFile = File(...), socket_id: str = Form(...)):
    # notify upload
    await sio.emit(
        "process_status",
        {"status": "file_uploaded", "message": f"{file.filename} uploaded"},
        to=socket_id,
    )

    await sio.emit(
        "process_status",
        {
            "status": "process_extraction_started",
            "message": "Process extraction started",
        },
        to=socket_id,
    )

    json_path = Path("sample_process_output.json")

    with open(json_path, "r", encoding="utf-8") as f:
        processes = json.load(f)

    await sio.emit(
        "process_status",
        {
            "status": "process_extraction_complete",
            "message": "Process extraction complete",
        },
        to=socket_id,
    )

    await sio.emit(
        "process_extracted",
        {
            "file": file.filename,
            "processes": processes,
        },
        to=socket_id,
    )

    return {
        "status": "success",
        "file": file.filename,
        "processes": processes,
    }


@sio.event
async def chat_message(sid, data):
    """
    Mock chat endpoint.
    Receives:
    {
        "message": "..."
    }
    """

    message = data.get("message", "")

    await asyncio.sleep(0.5)

    await sio.emit(
        "chat_response",
        {"message": f"Mock response for: {message}"},
        to=sid,
    )


# ----------------------------------------------------
# Static frontend assets
# ----------------------------------------------------
app.mount("/css", StaticFiles(directory="../frontend/css"), name="css")

app.mount("/js", StaticFiles(directory="../frontend/js"), name="js")


# ----------------------------------------------------
# Homepage
# ----------------------------------------------------
@app.get("/")
async def home():
    return FileResponse(Path("../frontend/index.html"))


# ----------------------------------------------------
# Socket.IO ASGI application
# ----------------------------------------------------
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

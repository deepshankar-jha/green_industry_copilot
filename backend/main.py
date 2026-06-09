from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Form
import asyncio

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
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), socket_id: str = Form(...)):
    contents = await file.read()

    # ----------------------------------------------------
    # Create a dedicated folder for this client
    # uploads/<socket_id>/
    # ----------------------------------------------------
    client_upload_dir = UPLOAD_DIR / socket_id
    client_upload_dir.mkdir(parents=True, exist_ok=True)

    # Full path to uploaded file
    filepath = client_upload_dir / file.filename

    # Save file
    with open(filepath, "wb") as f:
        f.write(contents)

    # notify file uploaded
    await sio.emit(
        "process_status",
        {"status": "file_uploaded", "message": f"{file.filename} uploaded"},
        to=socket_id,
    )

    # extraction started
    await sio.emit(
        "process_status",
        {
            "status": "process_extraction_started",
            "message": "Process extraction started",
        },
        to=socket_id,
    )

    # run extraction
    processes = await asyncio.to_thread(extractor.extract_processes, str(filepath))

    # extraction complete
    await sio.emit(
        "process_status",
        {
            "status": "process_extraction_complete",
            "message": "Process extraction complete",
        },
        to=socket_id,
    )

    # send to every connected client
    await sio.emit(
        "process_extracted",
        {"file": file.filename, "processes": processes},
        to=socket_id,
    )

    return {"status": "success", "file": file.filename}


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

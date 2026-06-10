from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Form
import asyncio

import json
from pathlib import Path
from process_extractor import ProcessExtractor
from process_optimizer import ProcessOptimizer
from socket_server import sio

from pydantic import BaseModel


class OptimizeRequest(BaseModel):
    processes: list[dict]
    query: str
    socket_id: str


import socketio

extractor = ProcessExtractor()
optimizer = ProcessOptimizer()
app = FastAPI()

# ----------------------------------------------------
# Upload directory
# ----------------------------------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ----------------------------------------------------
# Real file upload endpoint
# ----------------------------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), socket_id: str = Form(...)):

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

    # ----------------------------------------------------
    # Create folder for this socket connection
    # uploads/<socket_id>/
    # ----------------------------------------------------
    user_dir = UPLOAD_DIR / socket_id
    user_dir.mkdir(parents=True, exist_ok=True)

    # uploaded document path
    file_path = user_dir / file.filename

    # save uploaded document
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # extract processes
        processes = await asyncio.to_thread(extractor.extract_processes, str(file_path))

        # ----------------------------------------------------
        # Save extracted JSON with same filename
        #
        # example:
        # report.docx -> report.json
        # process.pdf -> process.json
        # ----------------------------------------------------
        json_path = user_dir / "original_graph.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(processes, f, indent=4, ensure_ascii=False)

        await sio.emit(
            "process_status",
            {
                "status": "process_extraction_complete",
                "message": "Process extraction complete",
            },
            to=socket_id,
        )

        # send extracted result to frontend
        await sio.emit(
            "process_extracted",
            {
                "file": file.filename,
                "json_file": json_path.name,
                "processes": processes,
            },
            to=socket_id,
        )

        return {
            "status": "success",
            "file": file.filename,
            "json_file": json_path.name,
            "processes": processes,
        }

    except Exception as e:

        await sio.emit(
            "process_status",
            {"status": "process_extraction_failed", "message": str(e)},
            to=socket_id,
        )

        return {"status": "error", "message": str(e)}


# ----------------------------------------------------
# Mock File upload endpoint
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

    # load mock process data
    json_path = Path("./uploads/mock/original_graph.json")

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

    # send extracted result to frontend
    await sio.emit(
        "process_extracted",
        {
            "file": file.filename,
            "json_file": json_path.name,
            "processes": processes,
        },
        to=socket_id,
    )

    # return exactly the same structure as /upload
    return {
        "status": "success",
        "file": file.filename,
        "json_file": json_path.name,
        "processes": processes,
    }


@app.post("/optimize")
async def optimize_graph(req: OptimizeRequest):

    optimized_processes = await asyncio.to_thread(
        optimizer.optimize_processes, req.processes
    )

    # ----------------------------------------------------
    # Save optimized graph
    # uploads/<socket_id>/optimized_graph.json
    # ----------------------------------------------------
    user_dir = UPLOAD_DIR / req.socket_id
    user_dir.mkdir(parents=True, exist_ok=True)

    optimized_graph_path = user_dir / "optimized_graph.json"

    with open(optimized_graph_path, "w", encoding="utf-8") as f:
        json.dump(optimized_processes, f, indent=4, ensure_ascii=False)

    return {"status": "success", "optimized_processes": optimized_processes}


# ----------------------------------------------------
# Mock optimize endpoint
# ----------------------------------------------------
@app.post("/mock-optimize")
async def mock_optimize(req: OptimizeRequest):

    json_path = Path("./uploads/mock/optimized_graph.json")

    with open(json_path, "r", encoding="utf-8") as f:
        optimized_processes = json.load(f)

    # return exactly the same structure as /optimize
    return {
        "status": "success",
        "optimized_processes": optimized_processes,
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

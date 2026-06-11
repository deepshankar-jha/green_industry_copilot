"""
main.py

Primary API entry point for the Process Intelligence platform.

Responsibilities
----------------
- Accept document uploads from clients.
- Extract process graphs from uploaded files.
- Store per-session process information.
- Upload graphs to FoundryIQ.
- Optimize extracted process graphs.
- Provide chat capabilities through Socket.IO.
- Serve frontend static assets.
- Expose FastAPI and Socket.IO applications.

Main Components
---------------
- ProcessExtractor:
    Converts uploaded documents into process graphs.

- ProcessOptimizer:
    Produces optimized versions of extracted processes.

- ChatManager:
    Maintains session state and handles conversational queries.

- FoundryIQManager:
    Uploads graph data for external analysis.

Session Storage
---------------
Each client session uses:

    uploads/<socket_id>/

containing:

    original_graph.json
    optimized_graph.json

Architecture
------------
Frontend
    ↓
FastAPI Endpoints
    ↓
Process Extraction / Optimization
    ↓
ChatManager + FoundryIQ
    ↓
Socket.IO Notifications
"""

from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Form
import asyncio
import json
from pathlib import Path
from socket_server import sio
from pydantic import BaseModel
import socketio

from process_extractor import ProcessExtractor
from process_optimizer import ProcessOptimizer
from chat_manager import ChatManager
from foundry_iq import FoundryIQManager


class OptimizeRequest(BaseModel):
    """
    Request model used by the optimization endpoint.

    Attributes
    ----------
    processes : list[dict]
        Process graph to optimize.

    query : str
        Optional optimization query from the client.

    socket_id : str
        Socket.IO session identifier used to maintain
        per-user state and event communication.
    """

    processes: list[dict]
    query: str
    socket_id: str


extractor = ProcessExtractor()
optimizer = ProcessOptimizer()
chat_manager = ChatManager()
foundry_iq = FoundryIQManager()

app = FastAPI()

# ----------------------------------------------------
# Upload Storage Configuration
#
# Creates the root directory used for storing
# session-specific files and graph JSON documents.
#
# Structure:
#
# uploads/
#     <socket_id>/
#         original_graph.json
#         optimized_graph.json
# ----------------------------------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ----------------------------------------------------
# Real file upload endpoint
# ----------------------------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), socket_id: str = Form(...)):
    """
    Upload a document and extract process information.

    Workflow
    --------
    1. Save the uploaded file.
    2. Notify the frontend of upload status.
    3. Extract processes from the document.
    4. Store the original graph in memory.
    5. Persist the graph as JSON.
    6. Upload the graph to FoundryIQ.
    7. Send extraction results back through Socket.IO.

    Parameters
    ----------
    file : UploadFile
        Document provided by the user.

    socket_id : str
        Socket.IO session identifier.

    Returns
    -------
    dict
        Success response containing:

        - status
        - filename
        - JSON filename
        - extracted processes

    Raises
    ------
    Exception
        Any extraction or upload failures are returned
        as error responses and emitted to the client.
    """

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

        # store original graph in session
        chat_manager.update_original_graph(socket_id, processes)

        # ----------------------------------------------------
        # Save extracted JSON with same filename
        #
        # example:
        # report.docx -> report.json
        # process.pdf -> process.json
        # ----------------------------------------------------
        json_path = user_dir / "original_graph.json"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                processes,
                f,
                indent=1,
                ensure_ascii=False,
                separators=(",", ":"),
            )

        await asyncio.to_thread(foundry_iq.upload_graph, str(json_path), socket_id)

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
    """
    Simulate file upload using predefined process data.

    Intended for development and testing.

    Instead of performing document extraction,
    the endpoint loads a mock graph from:

        uploads/mock/original_graph.json

    and returns the same response structure as
    the real upload endpoint.

    Parameters
    ----------
    file : UploadFile
        Placeholder uploaded file.

    socket_id : str
        Client Socket.IO session identifier.

    Returns
    -------
    dict
        Mock extraction result.
    """
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

        await asyncio.to_thread(foundry_iq.upload_graph, str(json_path), socket_id)

        chat_manager.update_original_graph(socket_id, processes)

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
    """
    Optimize an existing process graph.

    Workflow
    --------
    1. Run ProcessOptimizer.
    2. Save optimized graph in ChatManager.
    3. Persist optimized graph to disk.
    4. Upload graph to FoundryIQ.

    Parameters
    ----------
    req : OptimizeRequest
        Optimization request payload.

    Returns
    -------
    dict
        Contains the optimized process graph.
    """

    optimized_processes = await asyncio.to_thread(
        optimizer.optimize_processes, req.processes
    )

    # save optimized graph in memory
    chat_manager.update_optimized_graph(req.socket_id, optimized_processes)

    # ----------------------------------------------------
    # Save optimized graph
    # uploads/<socket_id>/optimized_graph.json
    # ----------------------------------------------------
    user_dir = UPLOAD_DIR / req.socket_id
    user_dir.mkdir(parents=True, exist_ok=True)

    optimized_graph_path = user_dir / "optimized_graph.json"

    with open(optimized_graph_path, "w", encoding="utf-8") as f:
        json.dump(
            optimized_processes,
            f,
            indent=1,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    await asyncio.to_thread(
        foundry_iq.upload_graph, str(optimized_graph_path), req.socket_id
    )

    return {"status": "success", "optimized_processes": optimized_processes}


# ----------------------------------------------------
# Mock optimize endpoint
# ----------------------------------------------------
@app.post("/mock-optimize")
async def mock_optimize(req: OptimizeRequest):
    """
    Load and return a predefined optimized graph.

    Used for development and UI testing.

    Reads:

        uploads/mock/optimized_graph.json

    and returns the same response format as the
    production optimization endpoint.

    Parameters
    ----------
    req : OptimizeRequest
        Request containing the client session id.

    Returns
    -------
    dict
        Mock optimization response.
    """
    json_path = Path("./uploads/mock/optimized_graph.json")

    with open(json_path, "r", encoding="utf-8") as f:
        optimized_processes = json.load(f)
    await asyncio.to_thread(foundry_iq.upload_graph, str(json_path), req.socket_id)

    chat_manager.update_optimized_graph(req.socket_id, optimized_processes)

    # return exactly the same structure as /optimize
    return {
        "status": "success",
        "optimized_processes": optimized_processes,
    }


@sio.event
async def chat_message(sid, data):
    """
    Handle incoming chat messages.

    Receives a message from a connected client,
    forwards it to ChatManager, and sends the
    generated response back through Socket.IO.

    Parameters
    ----------
    sid : str
        Socket.IO client identifier.

    data : dict
        Incoming payload expected to contain:

            {
                "message": "<user message>"
            }

    Emits
    -----
    chat_response
        Response generated by ChatManager.

    Error Handling
    --------------
    Exceptions are logged and returned to the
    client as error messages.
    """
    try:
        message = data.get("message", "")

        response = await chat_manager.chat(sid, message)

        await sio.emit("chat_response", {"message": response}, to=sid)

    except Exception as e:
        import traceback

        traceback.print_exc()

        await sio.emit("chat_response", {"message": f"[ERROR] {str(e)}"}, to=sid)


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
    """
    Serve the frontend application's entry page.

    Returns
    -------
    FileResponse
        index.html from the frontend directory.
    """
    return FileResponse(Path("../frontend/index.html"))


# ----------------------------------------------------
# Socket.IO ASGI Application
#
# Combines FastAPI HTTP endpoints with Socket.IO
# real-time communication into a single ASGI app.
#
# Handles:
#     - HTTP requests
#     - WebSocket connections
#     - Event emissions
#     - Chat interactions
#     - Process status notifications
# ----------------------------------------------------
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

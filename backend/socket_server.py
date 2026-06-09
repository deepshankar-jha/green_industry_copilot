"""
socket_server.py

Socket.IO backend server implementation.

This module provides real-time communication between the frontend
and backend using Socket.IO. It handles:

- Client connection and disconnection events.
- File upload progress notifications.
- Chat message processing.
- Sending responses and status updates to connected clients.

Communication is asynchronous and uses the ASGI interface,
making it suitable for integration with FastAPI.
"""

import socketio

# --------------------------------------------------------------------
# Socket.IO Server Configuration
# --------------------------------------------------------------------
# Create an asynchronous Socket.IO server that works with ASGI
# applications and allows requests from any origin.
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# --------------------------------------------------------------------
# Connection Events
# --------------------------------------------------------------------
@sio.event
async def connect(sid, environ):
    """
    Handle a new client connection.

    Parameters
    ----------
    sid : str
        Unique session ID assigned to the connected client.

    environ : dict
        Connection environment containing request information.

    Notes
    -----
    This event is automatically triggered when a client establishes
    a Socket.IO connection with the server.
    """
    print("Client connected:", sid)


@sio.event
async def disconnect(sid):
    """
    Handle client disconnection.

    Parameters
    ----------
    sid : str
        Session ID of the disconnected client.

    Notes
    -----
    Triggered automatically when the client closes the connection
    or loses connectivity.
    """
    print("Client disconnected:", sid)

# --------------------------------------------------------------------
# File Upload Events
# --------------------------------------------------------------------
@sio.event
async def upload_started(sid, data):
    """
    Handle the start of a file upload operation.

    Parameters
    ----------
    sid : str
        Session ID of the requesting client.

    data : dict
        Metadata describing the upload request.

    Notes
    -----
    This function simulates upload progress and sends progress
    updates back to the same client.

    Emits
    -----
    upload_progress
        Contains the upload percentage.

    upload_complete
        Indicates that the upload has completed successfully.
    """
    print("Upload started:", data)

    for progress in [20, 40, 60, 80, 100]:
        await sio.emit("upload_progress", {"progress": progress}, to=sid)

    await sio.emit("upload_complete", {"status": "success"}, to=sid)


@sio.event
async def chat_message(sid, data):

    response = {"message": "Hello from backend"}

    await sio.emit("chat_response", response, to=sid)

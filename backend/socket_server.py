"""
socket_server.py

Socket.IO backend server implementation.

This module provides real-time communication between frontend clients
and the backend using Socket.IO over ASGI. It is responsible for:

- Managing client connections and disconnections.
- Tracking connected client sessions.
- Reporting file upload progress.
- Processing chat messages.
- Sending responses and status updates to specific clients.

The server is asynchronous and designed for integration with
FastAPI or other ASGI-compatible frameworks.
"""

import socketio

# ============================================================================
# Socket.IO Server Configuration
# ============================================================================

# Create an asynchronous Socket.IO server.
#
# Configuration:
# - async_mode="asgi":
#       Enables compatibility with ASGI applications such as FastAPI.
#
# - cors_allowed_origins="*":
#       Allows requests from any origin.
#
# - max_http_buffer_size:
#       Maximum size (1 GB) for incoming payloads.
#
# - ping_timeout:
#       Time (seconds) after which inactive clients are disconnected.
#
# - ping_interval:
#       Interval (seconds) between heartbeat packets.
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    max_http_buffer_size=1024 * 1024 * 1024,
    ping_timeout=300,
    ping_interval=25,
)
# ============================================================================
# Connected Client Registry
# ============================================================================

# Maps a browser socket ID (sid) to associated metadata.
#
# Example:
# {
#     "socket_id_123": {
#         "username": "alice",
#         "current_upload": "file.pdf"
#     }
# }
connected_clients = {}


# --------------------------------------------------------------------
# Connection Events
# --------------------------------------------------------------------
@sio.event
async def connect(sid, environ):
    """
    Handle a new client connection.

    This event is triggered automatically when a client establishes
    a Socket.IO connection.

    Parameters
    ----------
    sid : str
        Unique Socket.IO session identifier for the client.

    environ : dict
        ASGI/WGI environment information associated with the connection.

    Notes
    -----
    A metadata entry is created for the connected client.
    """
    print("Client connected:", sid)
    connected_clients[sid] = {}


@sio.event
async def disconnect(sid):
    """
    Handle client disconnection.

    This event is triggered when a client disconnects or the connection
    times out.

    Parameters
    ----------
    sid : str
        Unique Socket.IO session identifier.

    Notes
    -----
    The client entry is safely removed from the registry.
    """
    print("Client disconnected:", sid)
    connected_clients.pop(sid, None)


# ============================================================================
# File Upload Events
# ============================================================================
@sio.event
async def upload_started(sid, data):
    """
    Handle upload initialization events.

    Parameters
    ----------
    sid : str
        Socket.IO session identifier for the client.

    data : dict
        Metadata describing the upload request.

    Notes
    -----
    Sends an initial upload progress update back to the originating client.
    """
    print("Upload started:", data)
    await sio.emit("upload_progress", {"progress": 10}, to=sid)


# ============================================================================
# Chat Events
# ============================================================================
@sio.event
async def chat_message(sid, data):
    """
    Process incoming chat messages.

    Parameters
    ----------
    sid : str
        Socket.IO session identifier of the sender.

    data : dict
        Payload containing the user's message and any associated metadata.

    Notes
    -----
    Currently returns a static response. This handler can be extended
    to invoke AI models, database queries, or other backend services.
    """
    response = {"message": "Hello from backend"}
    await sio.emit("chat_response", response, to=sid)

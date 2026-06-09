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

# maps browser socket id -> metadata
connected_clients = {}

# --------------------------------------------------------------------
# Connection Events
# --------------------------------------------------------------------
@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)
    connected_clients[sid] = {}

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
    connected_clients.pop(sid, None)

# --------------------------------------------------------------------
# File Upload Events
# --------------------------------------------------------------------
@sio.event
async def upload_started(sid, data):
    print("Upload started:", data)
    await sio.emit("upload_progress", {"progress": 10}, to=sid)


@sio.event
async def chat_message(sid, data):
    response = {"message": "Hello from backend"}
    await sio.emit("chat_response", response, to=sid)
import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)


@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)


@sio.event
async def upload_started(sid, data):
    print("Upload started:", data)

    for progress in [20, 40, 60, 80, 100]:
        await sio.emit("upload_progress", {"progress": progress}, to=sid)

    await sio.emit("upload_complete", {"status": "success"}, to=sid)


@sio.event
async def chat_message(sid, data):

    response = {"message": "Hello from backend"}

    await sio.emit("chat_response", response, to=sid)

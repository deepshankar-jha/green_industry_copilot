/**
 * Handles Socket.IO communication with backend.
 */
class SocketManager {
  constructor(serverUrl) {
    this.serverUrl = serverUrl;
    this.socket = null;
  }

  connect() {
    this.socket = io(this.serverUrl);

    this.socket.on("connect", () => {
      console.log("Connected:", this.socket.id);
    });

    this.socket.on("disconnect", () => {
      console.log("Disconnected");
    });

    this.socket.on("reconnect", () => {
      console.log("Reconnected with new id:", this.socket.id);

      this.socket.on("connect_error", (err) => {
        console.error("Connect error:", err);
      });
    });
  }

  on(eventName, callback) {
    this.socket.on(eventName, callback);
  }

  emit(eventName, data) {
    this.socket.emit(eventName, data);
  }

  getSocketId() {
    return this.socket.id;
  }
}

/**
 * ============================================================================
 * Application
 * ============================================================================
 * Main frontend controller.
 *
 * Responsibilities:
 * - Initialize all components.
 * - Maintain socket connection.
 * - Handle UI events.
 * - Upload files.
 * - Receive backend events.
 * - Coordinate interactions between classes.
 * ============================================================================
 */

class Application {
  constructor() {
    this.uploader = null;
    this.socketManager = null;

    this.initialize();
  }

  initialize() {
    this.initializeUploader();

    this.initializeSocket();

    this.registerEvents();
  }

  initializeUploader() {
    this.uploader = new FileUploader({
      fileInput: "#files",
      chooseButton: "#chooseBtn",
      fileList: "#fileList",
      submitButton: "#submitBtn",
    });
  }

  initializeSocket() {
    this.socketManager = new SocketManager("http://localhost:8000");

    this.socketManager.connect();
  }

  registerEvents() {
    // submit button
    document
      .querySelector("#submitBtn")
      .addEventListener("click", () => this.uploadFiles());

    // backend events
    this.socketManager.on("upload_progress", (data) =>
      this.onUploadProgress(data),
    );

    this.socketManager.on("upload_complete", (data) =>
      this.onUploadComplete(data),
    );

    this.socketManager.on("chat_response", (data) => this.onChatResponse(data));
  }

  uploadFiles() {
    const files = this.uploader.getFiles();

    if (files.length === 0) {
      return;
    }

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Upload started");

        this.socketManager.emit("upload_started", {
          files: files.map((f) => f.name),
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }

  onUploadProgress(data) {
    console.log("Progress:", data.progress);

    // update progress bar here
  }

  onUploadComplete(data) {
    console.log("Upload complete");

    this.uploader.clear();
  }

  onChatResponse(data) {
    console.log("AI response:", data);

    // update chat window
  }
}

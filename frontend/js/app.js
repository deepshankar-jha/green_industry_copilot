/**
 * ============================================================================
 * Application
 * ============================================================================
 * Main frontend controller.
 *
 * Responsibilities:
 * - Initialize UI components.
 * - Maintain the Socket.IO connection.
 * - Register frontend event handlers.
 * - Upload a single selected file to the backend.
 * - Receive backend progress and chat events.
 * - Coordinate interactions between the uploader and socket manager.
 * ============================================================================
 */

class Application {
  constructor() {
    this.uploader = null;
    this.socketManager = null;

    this.initialize();
  }
  /**
   * Initializes the application and all required subsystems.
   *
   * Initialization order:
   * 1. Create the file uploader.
   * 2. Establish the socket connection.
   * 3. Register UI and backend event handlers.
   */
  initialize() {
    this.initializeUploader();

    this.initializeSocket();

    this.registerEvents();
  }

  /**
   * Creates the FileUploader instance used to manage
   * single-file selection and display.
   */
  initializeUploader() {
    this.uploader = new FileUploader({
      fileInput: "#files",
      chooseButton: "#chooseBtn",
      fileList: "#fileList",
      submitButton: "#submitBtn",
    });
  }

  /**
   * Creates and connects the SocketManager used for
   * realtime communication with the backend.
   */
  initializeSocket() {
    this.socketManager = new SocketManager("http://localhost:8000");

    this.socketManager.connect();
  }

  /**
   * Registers UI events and backend socket listeners.
   *
   * Listens for:
   * - Submit button clicks.
   * - Upload progress events.
   * - Upload completion events.
   * - AI chat responses.
   */
  registerEvents() {
    // submit button
    document
      .querySelector("#submitBtn")
      .addEventListener("click", () => this.uploadFile());

    // backend events
    this.socketManager.on("upload_progress", (data) =>
      this.onUploadProgress(data),
    );

    this.socketManager.on("upload_complete", (data) =>
      this.onUploadComplete(data),
    );

    this.socketManager.on("chat_response", (data) => this.onChatResponse(data));
  }

  /**
   * Uploads the currently selected file.
   *
   * Workflow:
   * 1. Retrieve the selected file from FileUploader.
   * 2. Abort if no file is selected.
   * 3. Create FormData containing only the first file.
   * 4. Send the file to the /upload endpoint.
   * 5. Notify the socket server that upload processing has started.
   *
   * Note:
   * Although getFile() returns an array, only the first
   * element is uploaded because the application now
   * supports single-file uploads.
   */
  uploadFile() {
    const file = this.uploader.getFile();

    if (!file) {
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Upload started");

        this.socketManager.emit("upload_started", {
          file: file.name,
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }

  /**
   * Handles upload progress events emitted by the backend.
   *
   * @param {Object} data
   * @param {number} data.progress Percentage completion.
   */
  onUploadProgress(data) {
    console.log("Progress:", data.progress);

    // update progress bar here
  }

  /**
   * Handles completion of file processing.
   *
   * Clears the uploader so another file can be selected.
   *
   * @param {Object} data Backend response payload.
   */
  onUploadComplete(data) {
    console.log("Upload complete");

    this.uploader.clear();
  }

  /**
   * Handles AI-generated responses received from the backend.
   *
   * @param {Object} data Response payload returned by the server.
   */
  onChatResponse(data) {
    console.log("AI response:", data);

    // update chat window
  }
}

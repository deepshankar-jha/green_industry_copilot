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

    this.originalGraph = null;
    this.optimizedGraph = null;

    this.originalRenderer = null;
    this.optimizedRenderer = null;

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

    this.registerBackButton();

    this.registerWorkspaceSwitcher();

    // create chat
    this.chat = new ChatUI("chatApp");
    this.initializeChatToggle();

    this.initializeProcessGraph();
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

    document.getElementById("optimizeTab").addEventListener("click", () => {
      this.optimizeProcessGraph(
        "Reduce emissions, energy consumption and maximize recycling",
      );
    });

    // backend events
    this.socketManager.on("upload_progress", (data) =>
      this.onUploadProgress(data),
    );

    this.socketManager.on("upload_complete", (data) =>
      this.onUploadComplete(data),
    );

    this.socketManager.on("chat_response", (data) => this.onChatResponse(data));

    this.socketManager.on("process_extracted", (data) =>
      this.onProcessExtracted(data),
    );

    this.socketManager.on("process_status", (data) =>
      this.onProcessStatus(data),
    );
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

    this.showProcessingOverlay();

    const formData = new FormData();

    formData.append("file", file);
    formData.append("socket_id", this.socketManager.getSocketId());

    fetch("/upload", {
      method: "POST",
      body: formData,
    }).catch((err) => {
      this.hideProcessingOverlay();
      console.error(err);
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

    this.chat.receiveMessage(data.message);
  }

  onProcessExtracted(data) {
    this.hideProcessingOverlay();
    // save original process list
    this.originalProcesses = data.processes;

    this.showDashboard();

    // give browser time to layout visible elements
    requestAnimationFrame(() => {
      this.originalGraph.resize();
      this.optimizedGraph.resize();
    });

    this.originalGraph.clear();
    this.originalRenderer.render(data.processes);

    this.optimizedGraph.clear();
    this.optimizedRenderer.render(data.optimized_processes || data.processes);
  }

  onProcessStatus(data) {
    console.log(`[${data.status}] ${data.message}`);
  }

  showDashboard() {
    document.getElementById("landingPage").classList.add("hidden");

    document.getElementById("dashboard").classList.remove("hidden");
  }

  showProcessingOverlay() {
    document.getElementById("processingOverlay").style.display = "flex";
  }

  hideProcessingOverlay() {
    document.getElementById("processingOverlay").style.display = "none";
  }

  registerBackButton() {
    document.getElementById("backBtn").addEventListener("click", () => {
      document.getElementById("dashboard").classList.add("hidden");

      document.getElementById("landingPage").classList.remove("hidden");
    });
  }

  registerWorkspaceSwitcher() {
    this.workspaceSelect = document.getElementById("workspaceSelect");

    this.workspaceSelect.addEventListener("change", () =>
      this.switchWorkspacePanel(),
    );
  }

  switchWorkspacePanel() {
    document
      .querySelectorAll(".workspace-view")
      .forEach((panel) => panel.classList.add("hidden"));

    switch (this.workspaceSelect.value) {
      case "original":
        document.getElementById("originalPanel").classList.remove("hidden");

        requestAnimationFrame(() => {
          this.originalGraph.resize();
        });

        break;

      case "optimized":
        document.getElementById("optimizedPanel").classList.remove("hidden");

        requestAnimationFrame(() => {
          this.optimizedGraph.resize();
        });

        break;
    }
  }

  initializeProcessGraph() {
    //
    // Original graph
    //
    this.originalGraph = new ProcessNodeGraph("originalGraphCanvas");

    this.originalRenderer = new ProcessGraphRenderer(this.originalGraph);

    //
    // Optimized graph
    //
    this.optimizedGraph = new ProcessNodeGraph("optimizedGraphCanvas");

    this.optimizedRenderer = new ProcessGraphRenderer(this.optimizedGraph);
  }

  optimizeProcessGraph(query) {
    this.showProcessingOverlay();

    fetch("/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        processes: this.originalProcesses,
        query: query,
        socket_id: this.socketManager.getSocketId(),
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        this.hideProcessingOverlay();

        this.optimizedGraph.clear();

        this.optimizedRenderer.render(data.optimized_processes);

        // automatically switch view
        this.workspaceSelect.value = "optimized";
        this.switchWorkspacePanel();
      });
  }

  initializeChatToggle() {
    const btn = document.getElementById("chatToggleBtn");
    const chat = document.getElementById("chatApp");

    btn.addEventListener("click", () => {
      chat.classList.toggle("collapsed");
    });
  }
}

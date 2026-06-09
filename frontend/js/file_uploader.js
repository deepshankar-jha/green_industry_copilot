/**
 * ============================================================================
 * FileUploader
 * ============================================================================
 * Handles single-file upload interactions for the landing page.
 *
 * Responsibilities:
 * - Opens the native file picker when the custom button is clicked.
 * - Allows the user to select a single file.
 * - Replaces any previously selected file with the new one.
 * - Displays the selected file name and size.
 * - Allows removing the selected file.
 * - Shows or hides the submit button depending on whether a file exists.
 * - Provides methods for retrieving and clearing the selected file.
 * ============================================================================
 */

class FileUploader {
  /**
   * Creates a FileUploader instance and caches required DOM elements.
   *
   * @param {Object} config Configuration object.
   * @param {string} config.fileInput Selector for the hidden file input element.
   * @param {string} config.chooseButton Selector for the custom "Choose File" button.
   * @param {string} config.fileList Selector for the container displaying file information.
   * @param {string} config.submitButton Selector for the upload/submit button.
   */
  constructor({ fileInput, chooseButton, fileList, submitButton }) {
    this.fileInput = document.querySelector(fileInput);
    this.chooseButton = document.querySelector(chooseButton);
    this.fileList = document.querySelector(fileList);
    this.submitButton = document.querySelector(submitButton);

    /**
     * Stores all uploaded files.
     * @type {File[]}
     */
    this.file = null;

    this.initialize();
  }

  /**
   * Initializes event listeners and sets the initial UI state.
   *
   * Responsibilities:
   * - Opens the file picker when the custom button is clicked.
   * - Processes file selection events.
   * - Clears the input value to allow re-selecting the same file.
   * - Updates submit button visibility.
   */
  initialize() {
    // Open native file picker when custom button is clicked.
    this.chooseButton.addEventListener("click", () => {
      this.fileInput.click();
    });

    // Handle newly selected files.
    this.fileInput.addEventListener("change", () => {
      this.addFiles(this.fileInput.files);

      // Clear input value so the same file can be selected again.
      this.fileInput.value = "";
    });

    // Initialize submit button visibility.
    this.updateSubmitButton();
  }

  /**
   * Stores the selected file.
   *
   * Only the first file is used. If a file already exists,
   * it is replaced by the newly selected file.
   *
   * @param {FileList} fileList Files returned by the input element.
   */
  addFiles(fileList) {
    this.file = fileList.length > 0 ? fileList[0] : null;
    this.render();
  }

  /**
   * Removes the currently selected file.
   *
   * This is equivalent to calling clear().
   */
  removeFile() {
    this.clear();
  }

  /**
   * Renders the file information in the UI.
   *
   * Responsibilities:
   * - Clears any previous UI content.
   * - Displays the selected file name and size.
   * - Creates a remove button for clearing the file.
   * - Updates submit button visibility.
   */
  render() {
    this.fileList.innerHTML = "";

    if (this.file) {
      const file = this.file;

      const div = document.createElement("div");
      div.className = "file-item";

      div.innerHTML = `
        <div class="file-info">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
        </div>
        <button class="remove-btn">✕</button>
    `;

      div.querySelector(".remove-btn").addEventListener("click", () => {
        this.clear();
      });

      this.fileList.appendChild(div);
    }

    this.updateSubmitButton();
  }

  /**
   * Controls submit button visibility.
   *
   * Rules:
   * - Show the button when a file is selected.
   * - Hide the button when no file is selected.
   */
  updateSubmitButton() {
    this.submitButton.style.display = this.file ? "inline-block" : "none";
  }

  /**
   * Returns the currently selected file.
   *
   * @returns {File|null} Selected file or null if no file exists.
   */
  getFile() {
    return this.file;
  }

  /**
   * Clears the selected file and refreshes the UI.
   */
  clear() {
    this.file = null;
    this.render();
  }
}
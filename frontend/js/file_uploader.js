/**
 * ============================================================================
 * FileUploader
 * ============================================================================
 *
 * Lightweight utility for managing single-file uploads on the landing page.
 *
 * Features:
 * - Opens the native file picker through a custom button.
 * - Supports selecting exactly one file.
 * - Replaces previously selected files automatically.
 * - Displays selected file name and size.
 * - Allows removing the current file.
 * - Updates button visibility based on upload state.
 * - Exposes methods for retrieving and clearing the selected file.
 *
 * Workflow:
 * Choose File → Select File → Render File Info → Submit or Remove
 *
 * Dependencies:
 * - Browser File API
 * - DOM APIs
 *
 * ============================================================================
 */

class FileUploader {
  /**
   * Creates a FileUploader instance and caches DOM elements.
   *
   * @param {Object} config Component configuration.
   * @param {string} config.fileInput Selector for the hidden file input.
   * @param {string} config.chooseButton Selector for the custom file button.
   * @param {string} config.fileList Selector for the file display container.
   * @param {string} config.submitButton Selector for the submit button.
   */
  constructor({ fileInput, chooseButton, fileList, submitButton }) {
    this.fileInput = document.querySelector(fileInput);
    this.chooseButton = document.querySelector(chooseButton);
    this.fileList = document.querySelector(fileList);
    this.submitButton = document.querySelector(submitButton);

    /**
     * Currently selected file.
     *
     * Only one file is supported at a time.
     *
     * @type {File|null}
     */
    this.file = null;

    this.initialize();
  }

  /**
   * Initializes component event handlers and synchronizes the UI.
   *
   * Responsibilities:
   * - Opens the native file picker.
   * - Processes file selections.
   * - Clears the input value to allow selecting the same file again.
   * - Sets the initial button visibility.
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
   * Stores the selected file and refreshes the interface.
   *
   * Only the first file in the FileList is used.
   * Any previously selected file is replaced.
   *
   * @param {FileList} fileList FileList returned by the input element.
   */
  addFiles(fileList) {
    this.file = fileList.length > 0 ? fileList[0] : null;
    this.render();
  }

  /**
   * Removes the current file.
   *
   * Convenience wrapper around clear().
   */
  removeFile() {
    this.clear();
  }

  /**
   * Rebuilds the file list UI.
   *
   * Responsibilities:
   * - Clears previous content.
   * - Creates file information elements.
   * - Displays file name and size.
   * - Adds a remove button.
   * - Updates button visibility.
   */
  render() {
    // Reset previously rendered content.
    this.fileList.innerHTML = "";

    // Render file information only when a file exists.
    if (this.file) {
      const file = this.file;

      // Container representing the selected file.
      const div = document.createElement("div");
      div.className = "file-item";

      div.innerHTML = `
        <div class="file-info">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
        </div>
        <button class="remove-btn">✕</button>
    `;

      // Remove the file when the close button is clicked.
      div.querySelector(".remove-btn").addEventListener("click", () => {
        this.clear();
      });

      this.fileList.appendChild(div);
    }

    /**
     * Updates the visibility of action buttons according to upload state.
     *
     * UI Rules:
     *
     * File selected:
     * - Hide the "Choose File" button.
     * - Show the "Submit File" button.
     *
     * No file selected:
     * - Show the "Choose File" button.
     * - Hide the "Submit File" button.
     */
    this.updateSubmitButton();
  }

  /**
   * Controls choose button and submit button visibility.
   *
   * Rules:
   * - When a file exists:
   *     hide "Choose File"
   *     show "Submit File"
   *
   * - When no file exists:
   *     show "Choose File"
   *     hide "Submit File"
   */
  updateSubmitButton() {
    if (this.file) {
      this.submitButton.style.display = "inline-block";

      this.chooseButton.style.display = "none";
    } else {
      this.submitButton.style.display = "none";

      this.chooseButton.style.display = "inline-block";
    }
  }

  /**
   * Returns the currently selected file.
   *
   * @returns {File|null}
   * Selected file or null if no file has been chosen.
   */
  getFile() {
    return this.file;
  }

  /**
   * Clears the selected file and refreshes the UI.
   *
   * This method:
   * - Removes the current file reference.
   * - Re-renders the file list.
   * - Restores the initial button state.
   */
  clear() {
    this.file = null;
    this.render();
  }
}

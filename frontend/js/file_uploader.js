/**
 * ============================================================================
 * FileUploader
 * ============================================================================
 * Handles file upload interactions for the landing page.
 *
 * Features:
 * - Opens the file picker when the custom button is clicked.
 * - Supports uploading multiple files.
 * - Displays uploaded file names and sizes.
 * - Allows removing individual files.
 * - Shows the submit button only when at least one file exists.
 * - Provides methods for retrieving and clearing uploaded files.
 * ============================================================================
 */

class FileUploader {
  /**
   * Creates a FileUploader instance.
   *
   * @param {Object} config - Configuration object.
   * @param {string} config.fileInput - Selector for the hidden file input.
   * @param {string} config.chooseButton - Selector for the "Choose Files" button.
   * @param {string} config.fileList - Selector for the file list container.
   * @param {string} config.submitButton - Selector for the submit button.
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
    this.files = [];

    this.initialize();
  }

  /**
   * Initializes event listeners and UI state.
   *
   * Responsibilities:
   * - Opens the file dialog when the custom button is clicked.
   * - Handles file selection events.
   * - Resets the input value so the same file can be selected again.
   * - Sets the initial submit button visibility.
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
   * Adds files to the internal file array.
   *
   * @param {FileList} fileList - Files selected by the user.
   */
  addFiles(fileList) {
    this.files.push(...Array.from(fileList));
    this.render();
  }

  /**
   * Removes a file from the list.
   *
   * @param {number} index - Index of the file to remove.
   */
  removeFile(index) {
    this.files.splice(index, 1);
    this.render();
  }

  /**
   * Renders the current list of uploaded files.
   *
   * For each file:
   * - Creates a file item element.
   * - Displays file name and size.
   * - Attaches a remove button handler.
   * - Appends the item to the file list container.
   */
  render() {
    this.fileList.innerHTML = "";

    this.files.forEach((file, index) => {
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
        this.removeFile(index);
      });

      this.fileList.appendChild(div);
    });

    this.updateSubmitButton();
  }

  /**
   * Controls visibility of the submit button.
   *
   * Rules:
   * - Visible when one or more files are present.
   * - Hidden when no files exist.
   */
  updateSubmitButton() {
    this.submitButton.style.display =
      this.files.length > 0 ? "inline-block" : "none";
  }

  /**
   * Returns all currently uploaded files.
   *
   * @returns {File[]} Array of uploaded files.
   */
  getFiles() {
    return this.files;
  }

  /**
   * Removes all files and refreshes the UI.
   */
  clear() {
    this.files = [];
    this.render();
  }
}
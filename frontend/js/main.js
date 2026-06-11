/**
 * @file main.js
 * @description
 * Application entry point.
 *
 * Waits until the DOM is fully loaded and then creates
 * the main Application instance. The instance is exposed
 * on the global `window` object to make it accessible
 * from the browser console and other modules if needed.
 */

/**
 * Initialize the application once the document has been loaded.
 */

document.addEventListener("DOMContentLoaded", () => {
  /**
   * Global application instance.
   *
   * @type {Application}
   */
  window.app = new Application();
});

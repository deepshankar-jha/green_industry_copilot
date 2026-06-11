/**
 * @file chat_ui.js
 * @description
 * Browser-based chat UI component responsible for:
 * - Rendering the chat interface
 * - Handling user input and events
 * - Displaying incoming and outgoing messages
 * - Managing loading/thinking state
 * - Automatically scrolling to the newest message
 *
 * Dependencies:
 * - DOM APIs
 * - Optional window.app.socketManager for server communication
 *
 * Usage:
 * const chat = new ChatUI("chatApp");
 */

/**
 * Chat user interface controller.
 *
 * Encapsulates all UI logic related to:
 * - Creating chat elements
 * - Event registration
 * - Sending messages
 * - Receiving messages
 * - Message rendering
 * - Loading indicator management
 * - Automatic scrolling
 *
 * Communication with the backend is delegated to
 * window.app.socketManager when available.
 */
class ChatUI {
  /**
   * Creates a new chat interface inside the specified container.
   *
   * Initializes the UI, caches frequently used DOM elements,
   * and registers event listeners.
   *
   * @param {string} containerId
   * ID of the DOM element that will contain the chat interface.
   */
  constructor(containerId) {
    this.container = document.getElementById(containerId);

    this.render();

    this.messagesArea = this.chat.querySelector(".chat-messages");
    this.inputField = this.chat.querySelector("input");
    this.sendButton = this.chat.querySelector("button");

    this.attachEvents();
  }
  /**
   * Renders the complete chat interface inside the container.
   *
   * Creates:
   * - Header section
   * - Message display area
   * - Text input field
   * - Send button
   *
   * Stores a reference to the root chat element for later use.
   *
   * @returns {void}
   */
  render() {
    this.container.innerHTML = `
            <div class="chat-container">
                <div class="chat-header">

                <span class="chat-title">
                    Communication Assistant
                </span>

                <div class="chat-thinking hidden">

                    <div class="chat-spinner"></div>

                    <span class="chat-thinking-text">
                        Thinking...
                    </span>

                </div>

            </div>

                <div class="chat-messages"></div>

                <div class="chat-input">
                    <input type="text" placeholder="Type a message...">
                    <button>Send</button>
                </div>
            </div>
        `;

    this.chat = this.container.querySelector(".chat-container");
  }

  /**
   * Registers UI event handlers.
   *
   * Supported events:
   * - Send button click
   * - Enter key press in the input field
   *
   * Both events trigger message submission.
   *
   * @returns {void}
   */
  attachEvents() {
    this.sendButton.addEventListener("click", () => {
      this.sendMessage();
    });

    this.inputField.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        this.sendMessage();
      }
    });
  }

  /**
   * Sends the contents of the input field.
   *
   * Workflow:
   * 1. Reads and trims the input text.
   * 2. Ignores empty messages.
   * 3. Displays the message in the UI.
   * 4. Clears the input box.
   * 5. Shows the thinking indicator.
   * 6. Emits a "chat_message" event through the
   *    application's socket manager.
   *
   * @returns {void}
   */
  sendMessage() {
    const text = this.inputField.value.trim();

    if (!text) return;

    this.addMessage(text, "user");

    this.inputField.value = "";
    this.showThinking();

    // Forward the message to the backend if a socket
    // connection has been initialized.
    if (window.app && window.app.socketManager) {
      window.app.socketManager.emit("chat_message", {
        message: text,
      });
    }
  }

  /**
   * Processes an incoming message from the bot.
   *
   * Adds the received text to the message area using the
   * bot message style.
   *
   * @param {string} text
   * Message received from the bot.
   *
   * @returns {void}
   */
  receiveMessage(text) {
    this.hideThinking();
    this.addMessage(text, "bot");
  }

  /**
   * Creates and displays a chat message.
   *
   * Applies the appropriate CSS class depending on the sender
   * and appends the message to the conversation area.
   * Automatically scrolls to the newest message.
   *
   * @param {string} text
   * Message text to display.
   *
   * @param {string} sender
   * Message origin. Expected values are:
   * - "user"
   * - "bot"
   *
   * @returns {void}
   */
  addMessage(text, sender) {
    const message = document.createElement("div");

    message.classList.add("message");

    // Apply sender-specific styling.
    if (sender === "user") {
      message.classList.add("user-message");
    } else {
      message.classList.add("bot-message");
    }

    message.textContent = text;

    this.messagesArea.appendChild(message);

    this.scrollToBottom();
  }

  /**
   * Scrolls the message area to the most recent message.
   *
   * Ensures newly added messages are visible without requiring
   * manual scrolling.
   *
   * @returns {void}
   */
  scrollToBottom() {
    this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
  }

  /**
   * Removes all messages from the chat window.
   *
   * Does not remove the chat interface itself or reset event
   * handlers.
   *
   * @returns {void}
   */
  clear() {
    this.messagesArea.innerHTML = "";
  }

  /**
   * Displays the "Thinking..." indicator.
   *
   * Used while waiting for a response from the server
   * or chatbot.
   *
   * @returns {void}
   */
  showThinking() {
    this.chat.querySelector(".chat-thinking").classList.remove("hidden");
  }

  /**
   * Hides the "Thinking..." indicator.
   *
   * Called when a response has been received and
   * normal message display resumes.
   *
   * @returns {void}
   */
  hideThinking() {
    this.chat.querySelector(".chat-thinking").classList.add("hidden");
  }
}

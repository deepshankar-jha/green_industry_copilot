/**
 * @module ChatUI
 * @description
 * A lightweight browser-based chat interface implemented as a single class.
 * The class encapsulates rendering, event handling, message management,
 * automatic scrolling, and a simulated bot response.
 *
 * Features:
 * - Dynamic UI generation
 * - User message input
 * - Enter key support
 * - Message display with user and bot styling
 * - Automatic scrolling
 * - Chat clearing capability
 *
 * Example:
 * const chat = new ChatUI("chatApp");
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
                    Communication Assistent
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
   * Sends the current contents of the input field.
   *
   * Removes surrounding whitespace, ignores empty messages,
   * adds the user's message to the conversation, clears the
   * input field, and generates a simulated bot reply.
   *
   * @returns {void}
   */
  sendMessage() {
    const text = this.inputField.value.trim();

    if (!text) return;

    this.addMessage(text, "user");

    this.inputField.value = "";

    // Demo bot response
    setTimeout(() => {
      this.receiveMessage(`You said: ${text}`);
    }, 500);
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
}

/**
 * Creates and initializes the chat interface.
 *
 * The chat UI will be rendered inside the HTML element whose
 * ID is "chatApp".
 *
 * @type {ChatUI}
 */
const chat = new ChatUI("chatApp");

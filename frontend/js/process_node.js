/**
 * @module ProcessNode
 *
 * Defines the ProcessNode class used by the process graph system.
 * A process node encapsulates position information together with
 * user-visible data such as title and description, and supports
 * arbitrary JSON metadata for application-specific information.
 */

/**
 * Represents a single node within a process graph.
 *
 * Each node maintains:
 * - A unique identifier.
 * - Position coordinates used by the renderer.
 * - A title displayed to the user.
 * - A descriptive text.
 * - Arbitrary metadata stored as a JSON object.
 */
class ProcessNode {
  /**
   * Creates a new process node.
   *
   * @param {Object} [options={}] Initialization options.
   * @param {number} [options.id=0]
   * Unique identifier of the node.
   *
   * @param {number} [options.x=0]
   * Horizontal position of the node.
   *
   * @param {number} [options.y=0]
   * Vertical position of the node.
   *
   * @param {string} [options.title="Node"]
   * Display title of the node.
   *
   * @param {string} [options.description=""]
   * Descriptive text associated with the node.
   *
   * @param {Object} [options.metaData={}]
   * Arbitrary JSON metadata associated with the node.
   */
  constructor({
    id = 0,
    x = 0,
    y = 0,
    title = "Node",
    description = "",
    metaData = {},
  } = {}) {
    /**
     * Unique identifier for the node.
     *
     * @type {number}
     */
    this.id = id;

    /**
     * X-coordinate of the node.
     *
     * @type {number}
     */
    this.x = x;
    /**
     * Y-coordinate of the node.
     *
     * @type {number}
     */
    this.y = y;

    /**
     * Human-readable node title.
     *
     * @type {string}
     */
    this.title = title;
    /**
     * Human-readable node description.
     *
     * @type {string}
     */
    this.description = description;

    /**
     * Application-specific metadata.
     *
     * The contents are unrestricted and may contain any
     * JSON-serializable information required by the system.
     *
     * @type {Object}
     */
    this.metaData = metaData;

    this.connections = [];
    this.width = 140;
    this.height = 60;

    this.showDetails = true;
    this.width = 220;
    this.height = 80;

    this.updateSize();
  }

  /**
   * Retrieves the title of the node.
   *
   * This value is typically used by graph renderers
   * and user interfaces.
   *
   * @returns {string}
   * Node title.
   */
  getTitle() {
    return this.title;
  }

  /**
   * Retrieves the descriptive text associated with the node.
   *
   * @returns {string}
   * Node description.
   */
  getDescription() {
    return this.description;
  }

  /**
   * Retrieves the metadata object associated with the node.
   *
   * Metadata may contain arbitrary JSON data used by higher-level
   * components or application logic.
   *
   * @returns {Object}
   * Metadata object.
   */
  getMetaData() {
    return this.metaData;
  }

  connectTo(node) {
    if (!this.connections.includes(node)) {
      this.connections.push(node);
    }
  }

  disconnectFrom(node) {
    this.connections = this.connections.filter((n) => n !== node);
  }

  render(ctx) {
    this.updateSize();

    this.width = Math.max(this.width, this.measureTitleWidth(ctx));

    //
    // Node colors
    //
    const bodyColor = "#EEF4EE";
    const borderColor = "#B8D7B6";
    const headerColor = "#2FA53F";
    const titleColor = "#ffffff";
    const textColor = "#1C4033";
    const mutedColor = "#5F7668";

    const radius = 12;

    //
    // Main body
    //
    ctx.fillStyle = bodyColor;
    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.roundRect(this.x, this.y, this.width, this.height, radius);
    ctx.fill();
    ctx.stroke();

    //
    // Header strip
    //
    ctx.fillStyle = headerColor;
    ctx.beginPath();
    ctx.roundRect(this.x, this.y, this.width, 40, radius);
    ctx.fill();

    //
    // Toggle button
    //
    ctx.fillStyle = "#274d86";
    ctx.beginPath();
    this.roundRect(ctx, this.x + 8, this.y + 10, 18, 18, 5);
    ctx.fill();

    ctx.fillStyle = "#ffffff";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.fillText(this.showDetails ? "-" : "+", this.x + 17, this.y + 19);

    //
    // Title
    //
    ctx.fillStyle = titleColor;
    ctx.font = "bold 16px Arial";
    ctx.fillText(this.title, this.x + this.width / 2, this.y + 22);

    if (!this.showDetails) return;

    //
    // Body text
    //
    ctx.fillStyle = textColor;
    ctx.font = "12px Arial";
    ctx.textAlign = "left";

    let y = this.y + 55;

    y = this.drawWrappedText(
      ctx,
      "Description: " + this.description,
      this.x + 12,
      y,
      this.width - 24,
      18,
    );

    ctx.fillStyle = mutedColor;

    for (const [key, value] of Object.entries(this.metaData)) {
      y = this.drawWrappedText(
        ctx,
        `${key}: ${value}`,
        this.x + 12,
        y,
        this.width - 24,
        18,
      );
    }
  }

  renderConnections(ctx) {
    ctx.strokeStyle = "#40c4ff";
    ctx.fillStyle = "#40c4ff";
    ctx.lineWidth = 3;

    for (const target of this.connections) {
      // start from bottom center of source node
      const x1 = this.x + this.width / 2;
      const y1 = this.y + this.height;

      // end at top center of target node
      const x2 = target.x + target.width / 2;
      const y2 = target.y;

      // vertical bezier
      const cy = (y1 + y2) / 2;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.bezierCurveTo(x1, cy, x2, cy, x2, y2);
      ctx.stroke();

      this.drawArrow(ctx, x2, y2);
    }
  }

  drawArrow(ctx, x, y) {
    ctx.beginPath();

    ctx.moveTo(x, y);
    ctx.lineTo(x - 6, y - 12);
    ctx.lineTo(x + 6, y - 12);

    ctx.closePath();
    ctx.fill();
  }

  contains(x, y) {
    return (
      x >= this.x &&
      x <= this.x + this.width &&
      y >= this.y &&
      y <= this.y + this.height
    );
  }

  toggleDetails() {
    this.showDetails = !this.showDetails;
    this.updateSize();
  }

  updateSize() {
    if (!this.showDetails) {
      this.width = 220;
      this.height = 60;
      return;
    }

    const lines = [];

    // description
    lines.push("Description: " + this.description);

    // metadata
    for (const [key, value] of Object.entries(this.metaData)) {
      lines.push(`${key}: ${value}`);
    }

    //
    // estimate required width
    //
    let maxLength = this.title.length;

    for (const line of lines) {
      maxLength = Math.max(maxLength, line.length);
    }

    // 8 pixels per character
    this.width = Math.max(220, maxLength * 8 + 30);

    // title + padding + text rows
    this.height = 60 + lines.length * 20 + 20;
  }

  isToggleButtonHit(x, y) {
    return (
      x >= this.x + 5 && x <= this.x + 21 && y >= this.y + 5 && y <= this.y + 21
    );
  }

  drawWrappedText(ctx, text, x, y, maxWidth, lineHeight) {
    const words = text.split(" ");
    let line = "";

    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + " ";
      const width = ctx.measureText(testLine).width;

      if (width > maxWidth && n > 0) {
        ctx.fillText(line, x, y);
        y += lineHeight;
        line = words[n] + " ";
      } else {
        line = testLine;
      }
    }

    ctx.fillText(line, x, y);

    return y + lineHeight;
  }

  measureTitleWidth(ctx) {
    ctx.save();
    ctx.font = "bold 16px Arial";
    const width = ctx.measureText(this.title).width;
    ctx.restore();

    return width + 50; // left/right padding
  }

  roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }
}

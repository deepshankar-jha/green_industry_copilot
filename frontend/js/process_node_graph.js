/**
 * ------------------------------------------------------------------------
 * ProcessNodeGraph Module
 * ------------------------------------------------------------------------
 *
 * Provides an interactive canvas-based node graph for industrial processes.
 *
 * Features:
 * - Add and remove process nodes.
 * - Create directed connections between nodes.
 * - Automatically place newly created nodes.
 * - Prevent node overlap during layout generation.
 * - Create child nodes relative to a parent node.
 * - Drag nodes.
 * - Pan the graph.
 * - Zoom in and out.
 * - Toggle display of node description and metadata.
 * - Render a background grid.
 * - Continuously render nodes and their connections.
 *
 * Node rendering and connection rendering are delegated to ProcessNode.
 * Connection ownership is maintained by individual nodes.
 *
 * The graph includes a simple automatic layout engine that searches
 * for available regions and positions downstream nodes below their
 * parent while avoiding collisions with existing nodes.
 */

class ProcessNodeGraph {
  /**
   * Creates a new process node graph.
   *
   * Initializes:
   * - Canvas and rendering context.
   * - Node collection.
   * - View transformation variables.
   * - Mouse interaction state.
   * - Event listeners.
   * - Rendering loop.
   *
   * @param {string} canvasId
   * ID of the HTML canvas element.
   */
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");

    this.nodes = [];

    this.nextNodeId = 1;

    this.scale = 1;
    this.offsetX = 0;
    this.offsetY = 0;

    this.dragNode = null;
    this.dragOffsetX = 0;
    this.dragOffsetY = 0;

    this.panning = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;

    this.nodeWidth = 140;
    this.nodeHeight = 60;

    this.resize();

    window.addEventListener("resize", () => this.resize());

    this.canvas.addEventListener("mousedown", (e) => this.onMouseDown(e));
    this.canvas.addEventListener("mousemove", (e) => this.onMouseMove(e));
    this.canvas.addEventListener("mouseup", (e) => this.onMouseUp(e));
    this.canvas.addEventListener("mouseleave", (e) => this.onMouseUp(e));
    this.canvas.addEventListener("wheel", (e) => this.onWheel(e));

    requestAnimationFrame(() => this.render());
  }

  /**
   * --------------------------------------------------------------------
   * Canvas Management
   * --------------------------------------------------------------------
   */

  /**
   * Resizes the canvas to fill the browser window.
   *
   * Called:
   * - During construction.
   * - Whenever the window size changes.
   */
  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();

    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  /**
   * --------------------------------------------------------------------
   * Node Management
   * --------------------------------------------------------------------
   */

  /**
   * Creates and adds a new node to the graph.
   *
   * @param {string} title
   * Node title.
   *
   * @param {string} description
   * Node description.
   *
   * @param {Object} [metaData={}]
   * JSON metadata associated with the node.
   *
   * @param {number} [x=100]
   * Node X coordinate. May be supplied explicitly or obtained from
   * the automatic layout engine.
   *
   * @param {number} [y=100]
   * Node Y coordinate. May be supplied explicitly or obtained from
   * the automatic layout engine.
   *
   * @returns {ProcessNode}
   * Newly created node.
   */
  addNode(title, description, metaData = {}, x = 100, y = 100) {
    const node = new ProcessNode({
      id: this.nextNodeId++,
      x,
      y,
      title,
      description,
      metaData,
    });

    this.nodes.push(node);

    return node;
  }

  /**
   * Removes a node from the graph.
   *
   * @param {number} id
   * Identifier of the node to remove.
   */
  removeNode(id) {
    this.nodes = this.nodes.filter((n) => n.id !== id);

    this.connections = this.connections.filter(
      (c) => c.from !== id && c.to !== id,
    );
  }

  /**
   * Creates a directed connection between two nodes.
   *
   * @param {number} fromId
   * Source node ID.
   *
   * @param {number} toId
   * Destination node ID.
   */
  connectNodes(fromId, toId) {
    const from = this.getNodeById(fromId);
    const to = this.getNodeById(toId);

    if (from && to) {
      from.connectTo(to);
    }
  }

  /**
   * Removes a directed connection between two nodes.
   *
   * Delegates the removal to the source node.
   *
   * @param {number} fromId
   * Source node ID.
   *
   * @param {number} toId
   * Destination node ID.
   */
  removeConnection(fromId, toId) {
    const from = this.getNodeById(fromId);
    const to = this.getNodeById(toId);

    if (from && to) {
      from.disconnectFrom(to);
    }
  }

  /**
   * Finds a node by its identifier.
   *
   * @param {number} id
   * Node ID.
   *
   * @returns {ProcessNode|null}
   * Matching node, or null if not found.
   */
  getNodeById(id) {
    return this.nodes.find((n) => n.id === id);
  }

  /**
   * --------------------------------------------------------------------
   * Coordinate Conversion
   * --------------------------------------------------------------------
   */

  /**
   * Converts screen coordinates into graph-space coordinates.
   *
   * Used to account for:
   * - Zoom level.
   * - View translation.
   *
   * @param {number} x
   * Screen X coordinate.
   *
   * @param {number} y
   * Screen Y coordinate.
   *
   * @returns {{x:number,y:number}}
   * Coordinates in graph space.
   */
  screenToWorld(x, y) {
    return {
      x: (x - this.offsetX) / this.scale,
      y: (y - this.offsetY) / this.scale,
    };
  }

  /**
   * Determines which node lies beneath a position.
   *
   * Nodes are searched from topmost to bottommost so that
   * overlapping nodes behave correctly.
   *
   * @param {number} x
   * World-space X coordinate.
   *
   * @param {number} y
   * World-space Y coordinate.
   *
   * @returns {ProcessNode|null}
   * Node under the cursor, if any.
   */
  hitNode(x, y) {
    for (let i = this.nodes.length - 1; i >= 0; i--) {
      if (this.nodes[i].contains(x, y)) {
        return this.nodes[i];
      }
    }

    return null;
  }

  /**
   * --------------------------------------------------------------------
   * Mouse Interaction
   * --------------------------------------------------------------------
   */

  /**
   * Handles mouse button presses.
   *
   * Supports:
   * - Toggling node details when the node toggle button is clicked.
   * - Starting node dragging when a node body is clicked.
   * - Starting canvas panning when empty space is clicked.
   *
   * @param {MouseEvent} e
   * Mouse event.
   */
  onMouseDown(e) {
    const p = this.screenToWorld(e.offsetX, e.offsetY);

    const node = this.hitNode(p.x, p.y);

    if (node) {
      if (node.isToggleButtonHit(p.x, p.y)) {
        node.toggleDetails();
        return;
      }
      this.dragNode = node;

      this.dragOffsetX = p.x - node.x;
      this.dragOffsetY = p.y - node.y;
    } else {
      this.panning = true;

      this.lastMouseX = e.offsetX;
      this.lastMouseY = e.offsetY;
    }
  }

  /**
   * Handles mouse movement.
   *
   * Updates:
   * - Node positions during dragging.
   * - View offset during panning.
   *
   * @param {MouseEvent} e
   * Mouse event.
   */
  onMouseMove(e) {
    const p = this.screenToWorld(e.offsetX, e.offsetY);

    if (this.dragNode) {
      this.dragNode.x = p.x - this.dragOffsetX;
      this.dragNode.y = p.y - this.dragOffsetY;
    }

    if (this.panning) {
      this.offsetX += e.offsetX - this.lastMouseX;
      this.offsetY += e.offsetY - this.lastMouseY;

      this.lastMouseX = e.offsetX;
      this.lastMouseY = e.offsetY;
    }
  }

  /**
   * Stops:
   * - Node dragging.
   * - Graph panning.
   */
  onMouseUp() {
    this.dragNode = null;
    this.panning = false;
  }

  /**
   * Handles zooming with the mouse wheel.
   *
   * Scroll up:
   * - Zoom in.
   *
   * Scroll down:
   * - Zoom out.
   *
   * @param {WheelEvent} e
   * Mouse wheel event.
   */
  onWheel(e) {
    e.preventDefault();

    const zoomFactor = 1.1;

    if (e.deltaY < 0) this.scale *= zoomFactor;
    else this.scale /= zoomFactor;
  }

  /**
   * --------------------------------------------------------------------
   * Rendering
   * --------------------------------------------------------------------
   */

  /**
   * Draws the background grid.
   *
   * The grid automatically adapts to:
   * - Current zoom level.
   * - Current pan offset.
   */
  drawGrid() {
    const size = 50;

    const width = this.canvas.width;
    const height = this.canvas.height;

    this.ctx.strokeStyle = "#333";
    this.ctx.lineWidth = 1;

    const startX = -this.offsetX / this.scale;
    const startY = -this.offsetY / this.scale;

    for (
      let x = Math.floor(startX / size) * size;
      x < startX + width / this.scale;
      x += size
    ) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, startY);
      this.ctx.lineTo(x, startY + height / this.scale);
      this.ctx.stroke();
    }

    for (
      let y = Math.floor(startY / size) * size;
      y < startY + height / this.scale;
      y += size
    ) {
      this.ctx.beginPath();
      this.ctx.moveTo(startX, y);
      this.ctx.lineTo(startX + width / this.scale, y);
      this.ctx.stroke();
    }
  }

  /**
   * Main rendering loop.
   *
   * Rendering order:
   * 1. Clear canvas.
   * 2. Apply view transformations.
   * 3. Draw grid.
   * 4. Draw node connections.
   * 5. Draw nodes.
   * 6. Schedule next frame.
   *
   * Runs continuously using requestAnimationFrame().
   */
  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.ctx.save();

    this.ctx.translate(this.offsetX, this.offsetY);
    this.ctx.scale(this.scale, this.scale);

    this.drawGrid();

    // draw connections first
    for (const node of this.nodes) {
      node.renderConnections(this.ctx);
    }

    // draw nodes on top
    for (const node of this.nodes) {
      node.render(this.ctx);
    }

    this.ctx.restore();

    requestAnimationFrame(() => this.render());
  }

  /**
   * --------------------------------------------------------------------
   * Automatic Node Placement
   * --------------------------------------------------------------------
   *
   * Provides helper functions for automatically positioning new nodes.
   *
   * Layout strategy:
   * - Child nodes are initially placed below their parent.
   * - Occupied regions are detected using bounding-box overlap tests.
   * - If the target location is occupied, the search continues downward.
   * - Excessively tall columns are wrapped into additional columns.
   * - Spacing between nodes is preserved through configurable padding.
   */

  /**
   * Determines whether a rectangular area intersects any existing node.
   *
   * Used by the automatic layout engine to avoid overlapping nodes.
   *
   * A configurable padding region is added around nodes to preserve
   * spacing between neighbouring nodes.
   *
   * @param {number} x
   * Candidate X coordinate.
   *
   * @param {number} y
   * Candidate Y coordinate.
   *
   * @param {number} width
   * Width of the area being tested.
   *
   * @param {number} height
   * Height of the area being tested.
   *
   * @param {number} [padding=40]
   * Additional clearance around nodes.
   *
   * @returns {boolean}
   * True if the area intersects an existing node.
   */
  isAreaOccupied(x, y, width, height, padding = 60) {
    for (const node of this.nodes) {
      const left1 = x;
      const right1 = x + width;
      const top1 = y;
      const bottom1 = y + height;

      const left2 = node.x - padding;
      const right2 = node.x + node.width + padding;
      const top2 = node.y - padding;
      const bottom2 = node.y + node.height + padding;

      if (
        left1 < right2 &&
        right1 > left2 &&
        top1 < bottom2 &&
        bottom1 > top2
      ) {
        return true;
      }
    }

    return false;
  }

  /**
   * Searches for an unoccupied position suitable for placing a node.
   *
   * Starting from the supplied coordinates, the search proceeds
   * vertically until an empty region is found.
   *
   * If a column exceeds the maximum search height, the algorithm
   * wraps into a new column and continues searching.
   *
   * This provides a simple collision-free layout mechanism without
   * requiring manual coordinates.
   *
   * @param {number} startX
   * Initial search X coordinate.
   *
   * @param {number} startY
   * Initial search Y coordinate.
   *
   * @returns {{x:number,y:number}}
   * First available position.
   */
  findFreePosition(startX, startY, width = 320, height = 220) {
    const verticalGap = 100;
    const horizontalGap = 120;

    let x = startX;
    let y = startY;

    while (true) {
      if (!this.isAreaOccupied(x, y, width, height)) {
        return { x, y };
      }

      y += height + verticalGap;

      if (y > 2500) {
        y = startY;
        x += width + horizontalGap;
      }
    }
  }

  /**
   * Computes the preferred position for the next child node.
   *
   * The search begins beneath the supplied parent node and delegates
   * collision avoidance to findFreePosition().
   *
   * Child nodes are therefore arranged in a top-to-bottom flow while
   * maintaining adequate spacing between neighbouring branches.
   *
   * @param {ProcessNode} parentNode
   * Parent node whose successor is being placed.
   *
   * @returns {{x:number,y:number}}
   * Coordinates for the new node.
   */
  placeNextNode(parentNode) {
    const childIndex = parentNode.connections.length;

    // spacing between sibling branches
    const horizontalSpacing = 500;
    const verticalSpacing = 220;

    // center siblings around the parent
    const x =
      parentNode.x +
      (childIndex - (Math.max(parentNode.connections.length, 1) - 1) / 2) *
        horizontalSpacing;

    const y = parentNode.y + parentNode.height + verticalSpacing;

    return this.findFreePosition(x, y);
  }

  /**
   * Creates a new node as a child of the specified parent.
   *
   * The node position is determined automatically and the new node
   * is immediately connected to its parent.
   *
   * This provides a convenient way to build process chains without
   * manually calculating coordinates.
   *
   * @param {ProcessNode} parentNode
   * Source node.
   *
   * @param {string} title
   * Node title.
   *
   * @param {string} description
   * Node description.
   *
   * @param {Object} [metaData={}]
   * Additional metadata associated with the node.
   *
   * @returns {ProcessNode}
   * Newly created and connected node.
   */
  addNextNode(parentNode, title, description, metaData = {}) {
    const pos = this.placeNextNode(parentNode);

    const node = this.addNode(title, description, metaData, pos.x, pos.y);

    parentNode.connectTo(node);

    return node;
  }

  clear() {
    this.nodes = [];

    this.nextNodeId = 1;
  }
}

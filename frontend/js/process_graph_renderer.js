/**
 * --------------------------------------------------------------------------
 * ProcessGraphRenderer
 * --------------------------------------------------------------------------
 * Responsible for converting process definitions into a visual node graph.
 *
 * Features:
 * - Builds lookup tables for fast process access.
 * - Detects root processes automatically.
 * - Supports cyclic graphs by selecting a fallback root.
 * - Recursively creates nodes and edges.
 * - Prevents duplicate node creation.
 * - Generates formatted metadata for display inside graph nodes.
 */
class ProcessGraphRenderer {
  /**
   * Create a new renderer.
   *
   * @param {ProcessNodeGraph} graph
   *        Graph implementation responsible for creating and connecting nodes.
   */
  constructor(graph) {
    this.graph = graph;

    /**
     * Maps process names to their process definitions.
     *
     * @type {Map<string, Object>}
     */
    this.processMap = new Map();

    /**
     * Maps process names to already-created graph nodes.
     * Used to avoid duplicate nodes and handle cyclic graphs.
     *
     * @type {Map<string, ProcessNode>}
     */
    this.nodeMap = new Map();
  }

  /**
   * Render an entire process list into the graph.
   *
   * Rendering steps:
   * 1. Build process lookup tables.
   * 2. Determine root nodes.
   * 3. Handle cyclic graphs when no roots exist.
   * 4. Create root nodes.
   * 5. Recursively render descendants.
   *
   * @param {Array<Object>} processes
   *        Collection of process definitions.
   */
  render(processes) {
    this.processMap.clear();
    this.nodeMap.clear();

    // Build fast lookup table for process definitions.
    for (const process of processes) {
      this.processMap.set(process.process_name, process);
    }

    // Collect all child process names to identify roots.
    const childNames = new Set();

    for (const process of processes) {
      for (const childName of process.next_processes || []) {
        childNames.add(childName);
      }
    }

    let roots = processes.filter((p) => !childNames.has(p.process_name));

    // Fallback root for cyclic graphs where no natural root exists.
    if (roots.length === 0 && processes.length > 0) {
      roots = [processes[0]];
    }

    let startX = 200;

    for (const root of roots) {
      const rootNode = this.createNode(root, startX, 100);

      this.renderChildren(rootNode, root);

      startX += 700;
    }
  }

  /**
   * Recursively render all children of a process node.
   *
   * Existing nodes are reused to prevent duplicate creation
   * and to support graphs containing cycles or shared branches.
   *
   * Missing process references are reported via console warnings.
   *
   * @param {ProcessNode} parentNode
   *        Parent graph node.
   *
   * @param {Object} process
   *        Source process definition.
   */
  renderChildren(parentNode, process) {
    for (const childName of process.next_processes || []) {
      const childProcess = this.processMap.get(childName);

      if (!childProcess) {
        console.warn(
          `Process ${process.process_name} references missing process ${childName}`,
        );
        continue;
      }

      let childNode;

      if (this.nodeMap.has(childName)) {
        childNode = this.nodeMap.get(childName);
        parentNode.connectTo(childNode);
      } else {
        childNode = this.graph.addNextNode(
          parentNode,
          childProcess.process_name,
          childProcess.description,
          this.createMetaData(childProcess),
        );

        this.nodeMap.set(childName, childNode);

        this.renderChildren(childNode, childProcess);
      }
    }
  }

  /**
   * Create a graph node representing a process.
   *
   * Newly created nodes are stored in the node map
   * for future reuse and cycle detection.
   *
   * @param {Object} process
   *        Process definition.
   *
   * @param {number} [x=100]
   *        Initial x-coordinate.
   *
   * @param {number} [y=100]
   *        Initial y-coordinate.
   *
   * @returns {ProcessNode}
   *          Created graph node.
   */
  createNode(process, x = 100, y = 100) {
    const node = this.graph.addNode(
      process.process_name,
      process.description,
      this.createMetaData(process),
      x,
      y,
    );

    this.nodeMap.set(process.process_name, node);

    return node;
  }

  /**
   * Generate formatted metadata used for node display.
   *
   * Converts arrays of inputs, outputs, byproducts,
   * energy consumption, water usage, and emissions into
   * human-readable strings suitable for graph labels.
   *
   * @param {Object} process
   *        Process definition.
   *
   * @returns {Object<string, string|number>}
   *          Structured metadata object containing:
   *          - Inputs
   *          - Outputs
   *          - Byproducts
   *          - Energy
   *          - Water
   *          - Emissions
   *          - Cost
   */
  createMetaData(process) {
    return {
      Inputs: process.inputs
        .map((i) => `${i.name}: ${i.quantity} ${i.measuring_unit}`)
        .join("\n"),

      Outputs: process.outputs
        .map((o) => `${o.name}: ${o.quantity} ${o.measuring_unit}`)
        .join("\n"),

      Byproducts: process.byproducts
        .map((b) => `${b.name}: ${b.quantity} ${b.measuring_unit}`)
        .join("\n"),

      Energy: process.energy_consumption
        .map((e) => `${e.quantity} ${e.measuring_unit} (${e.energy_source})`)
        .join("\n"),

      Water: process.water_consumption
        .map((w) => `${w.water_source}: ${w.quantity} ${w.measuring_unit}`)
        .join("\n"),

      Emissions: process.emissions
        .map((e) => `${e.name}: ${e.quantity} ${e.measuring_unit}`)
        .join("\n"),

      Cost: process.operating_cost,
    };
  }
}

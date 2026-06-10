/**
 * Converts process JSON into a ProcessNodeGraph.
 */
class ProcessGraphRenderer {
  constructor(graph) {
    this.graph = graph;

    // process_name -> process object
    this.processMap = new Map();

    // process_name -> ProcessNode
    this.nodeMap = new Map();
  }

  /**
   * Render entire process list.
   *
   * @param {Array<Object>} processes
   */
  render(processes) {
    this.processMap.clear();
    this.nodeMap.clear();

    // build lookup table
    for (const process of processes) {
      this.processMap.set(process.process_name, process);
    }

    // determine root nodes
    const childNames = new Set();

    for (const process of processes) {
      for (const childName of process.next_processes || []) {
        childNames.add(childName);
      }
    }

    let roots = processes.filter((p) => !childNames.has(p.process_name));

    // Handle cyclic graphs (no roots)
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
   * Recursively create child nodes.
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
   * Create graph node from process object.
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
   * Convert nested arrays into readable metadata.
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

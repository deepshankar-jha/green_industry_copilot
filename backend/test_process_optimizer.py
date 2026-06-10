"""
test_process_optimizer.py

Loads sample_process_output.json, optimizes the process graph using
ProcessOptimizer, and saves the result as
sample_optimized_process_output.json.
"""

import json

from process_optimizer import ProcessOptimizer

INPUT_FILE = "sample_process_output.json"
OUTPUT_FILE = "sample_optimized_process_output.json"


def main():
    # Create optimizer
    optimizer = ProcessOptimizer()

    # Load original graph
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        processes = json.load(f)

    print(f"Loaded {len(processes)} processes.")

    # Generate optimized graph
    optimized_processes = optimizer.optimize_processes(processes)

    print(f"Generated optimized graph with {len(optimized_processes)} processes.")

    # Save optimized graph
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(optimized_processes, f, indent=4, ensure_ascii=False)

    print(f"Optimized graph saved to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    main()

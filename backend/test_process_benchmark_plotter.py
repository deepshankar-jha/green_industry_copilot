# test_process_benchmark_plotter.py

from pathlib import Path
import shutil

from process_benchmark_plotter import ProcessBenchmarkPlotter


def main():

    # Input files
    original_json = "simulation_analytics_original.json"
    optimized_json = "simulation_analytics_optimized.json"

    # Output directories
    graphs_dir = Path("./graphs")
    summary_dir = Path("./summary")

    graphs_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)

    # Create plotter
    plotter = ProcessBenchmarkPlotter(
        original_json=original_json,
        optimized_json=optimized_json,
        output_dir=str(graphs_dir)
    )

    # Generate all benchmark graphs
    plotter.generate_all()

    # Create summary dataframe
    summary_df = plotter.create_summary_table()

    # Save summary CSV into ./summary
    summary_csv = summary_dir / "summary.csv"
    summary_df.to_csv(summary_csv)

    # Move the summary generated inside graphs directory
    generated_summary = graphs_dir / "summary.csv"
    if generated_summary.exists():
        generated_summary.unlink()

    print()
    print("Benchmark completed successfully.")
    print(f"Graphs saved to : {graphs_dir.resolve()}")
    print(f"Summary saved to: {summary_csv.resolve()}")


if __name__ == "__main__":
    main()
"""
test_process_graph_simulator.py

Example usage:

python test_process_graph_simulator.py \
    --input sample_process_output.json \
    --output simulation_analytics.json
"""

import json
import argparse

from process_graph_simulator import ProcessGraphSimulator


def main():

    parser = argparse.ArgumentParser(
        description="Run a process graph simulation and export analytics."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input process graph JSON file"
    )

    parser.add_argument(
        "--output",
        default="simulation_analytics.json",
        help="Output analytics JSON file"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days to simulate"
    )

    parser.add_argument(
        "--utilization",
        type=float,
        default=0.95,
        help="Average plant utilization"
    )

    parser.add_argument(
        "--variability",
        type=float,
        default=0.05,
        help="Daily variability factor"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed"
    )

    args = parser.parse_args()

    # Load process graph
    with open(args.input, "r") as f:
        process_graph = json.load(f)

    # Create simulator
    simulator = ProcessGraphSimulator(process_graph)

    # Run simulation
    analytics = simulator.simulate(
        days=args.days,
        utilization=args.utilization,
        variability=args.variability,
        random_seed=args.seed
    )

    # Save analytics
    with open(args.output, "w") as f:
        json.dump(analytics, f, indent=2)

    print(f"Simulation completed.")
    print(f"Analytics written to: {args.output}")

    # Print summary
    total_energy = 0.0
    total_water = 0.0

    for day in analytics["daily_series"]:
        total_energy += day["energy_consumption"].get("MWh", 0.0)
        total_water += day["water_usage"].get("m3", 0.0)

    print(f"Total energy consumption : {total_energy:.2f} MWh")
    print(f"Total water usage        : {total_water:.2f} m3")


if __name__ == "__main__":
    main()
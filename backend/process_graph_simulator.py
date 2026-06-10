import random
from datetime import datetime, timedelta
from collections import defaultdict

class ProcessGraphSimulator:
    def __init__(self, process_graph):
        self.process_graph = process_graph

    def simulate(self, days=365, utilization=0.95, variability=0.05, random_seed=42):

        random.seed(random_seed)

        start_date = datetime(2026, 1, 1)

        results = []

        for day in range(days):

            date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")

            energy = defaultdict(float)
            water = defaultdict(float)
            emissions = defaultdict(float)
            inputs = defaultdict(float)
            outputs = defaultdict(float)
            byproducts = defaultdict(float)

            daily_factor = utilization * random.uniform(
                1 - variability, 1 + variability
            )

            for process in self.process_graph:

                # Inputs
                for item in process.get("inputs", []):
                    inputs[item["name"]] += item["quantity"] * daily_factor

                # Outputs
                for item in process.get("outputs", []):
                    outputs[item["name"]] += item["quantity"] * daily_factor

                # Byproducts
                for item in process.get("byproducts", []):
                    byproducts[item["name"]] += item["quantity"] * daily_factor

                # Energy
                for item in process.get("energy_consumption", []):
                    energy["MWh"] += item["quantity"] * daily_factor

                # Water
                for item in process.get("water_consumption", []):
                    water["m3"] += item["quantity"] * daily_factor

                # Emissions
                for item in process.get("emissions", []):
                    emissions[item["name"]] += item["quantity"] * daily_factor

            results.append(
                {
                    "date": date,
                    "energy_consumption": dict(energy),
                    "water_usage": dict(water),
                    "raw_materials": dict(inputs),
                    "products": dict(outputs),
                    "byproducts": dict(byproducts),
                    "emissions": dict(emissions),
                }
            )

        return {
            "metadata": {
                "simulation_days": days,
                "utilization": utilization,
                "variability": variability,
            },
            "daily_series": results,
        }

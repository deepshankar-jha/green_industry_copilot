"""
process_optimizer.py

Uses an LLM to transform an existing industrial process graph into a
greener, lower-emission, lower-cost and more circular process network.
"""

import json
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from schemas import *

load_dotenv()


class ProcessOptimizer:
    """
    Generates a sustainable version of an existing process graph.

    Features
    --------
    - Reduce emissions.
    - Reduce energy consumption.
    - Replace fossil energy with renewable energy.
    - Recycle byproducts.
    - Recover waste heat.
    - Reuse water.
    - Introduce carbon capture.
    - Lower operating cost.
    - Add circular-economy links.
    - Preserve process ordering where practical.
    """

    def __init__(self, model: str = "gpt-5-mini"):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        self.llm = ChatOpenAI(model=model, temperature=0.2)

    def optimize_processes(self, processes: list[dict]) -> list[dict]:

        structured_llm = self.llm.with_structured_output(ProcessList)

        prompt = f"""
You are a sustainability and industrial process optimization expert.

Given an industrial process graph, redesign it to maximize:

1. Carbon reduction.
2. Energy efficiency.
3. Water conservation.
4. Circular economy principles.
5. Waste minimization.
6. Byproduct reuse.
7. Heat recovery.
8. Renewable energy usage.
9. Lower operating costs.
10. Reduced NOx, SOx, methane and particulate emissions.

Rules
-----

- Preserve overall product output.
- Preserve process connectivity.
- Add new processes if beneficial.
- Add recycle loops when appropriate.
- Reuse byproducts wherever possible.
- Replace fossil fuel energy sources with:

    - Solar
    - Wind
    - Green hydrogen
    - Biomass
    - Waste heat recovery

- Introduce:

    - Carbon capture
    - Water recycling
    - Catalyst improvements
    - Electrification
    - Membrane separation
    - Heat exchangers
    - Waste-to-energy systems

- Reduce emissions and costs whenever possible.

Return ONLY the optimized process graph.

Original graph:

{json.dumps(processes, indent=2)}
"""

        result = structured_llm.invoke(prompt)

        return [p.model_dump() for p in result.processes]

    def load_json(self, filepath: str):

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def optimize_file(self, filepath: str):

        processes = self.load_json(filepath)

        return self.optimize_processes(processes)

    def save_json(self, input_path: str, output_path: str):

        optimized = self.optimize_file(input_path)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(optimized, f, indent=4, ensure_ascii=False)

        return optimized

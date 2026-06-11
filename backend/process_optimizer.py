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

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=0,
            max_completion_tokens=30000,
        )

    def optimize_processes(self, processes: list[dict]) -> list[dict]:

        structured_llm = self.llm.with_structured_output(
            ProcessList, method="function_calling"
        )

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
- Preserve graph connectivity.
- Process names must be unique.
- next_processes MUST contain process names.
- Every name inside next_processes must exactly match an existing process_name.
- Use identical spelling, spacing and capitalization.
- Do not create orphan processes.
- Do not create dangling references.
- Maintain a valid directed graph.
- Add new processes if beneficial.
- Add recycle loops when appropriate.
- Reuse byproducts wherever possible.

Consistency Rules:

If a process_name is:

"Heat Treatment"

then every reference to it inside next_processes must be:

["Heat Treatment"]

NOT:

["heat treatment"]
["Heat-treatment"]
["Heat Treatment Process"]
["Heating"]

The process_name and its references inside next_processes must always match exactly.

Return ONLY the optimized process graph.

Original graph:

{json.dumps(processes, separators=(",", ":"))}
"""

        result = structured_llm.invoke(prompt)

        processes = [p.model_dump() for p in result.processes]

        return processes

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

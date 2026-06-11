"""
Simple test runner for ProcessExtractor.

Loads a document, extracts the process flow,
and saves the output to a JSON file.
"""

from pathlib import Path
from dotenv import load_dotenv
from process_extractor import ProcessExtractor
import json

load_dotenv()


def main():
    extractor = ProcessExtractor()

    input_file = "./test_data/Shakti AgroChem Industries Processes.pdf"

    processes = extractor.extract_processes(input_file)

    output_file = Path("sample_process_output.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processes, f, indent=4, ensure_ascii=False)

    print(f"Saved output to {output_file}")


if __name__ == "__main__":
    main()
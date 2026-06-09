"""
Simple test runner for ProcessExtractor.

Loads a document, extracts the process flow, and prints the
structured JSON output.
"""

from dotenv import load_dotenv
from process_extractor import ProcessExtractor
import json

# Load environment variables (.env)
load_dotenv()


def main():
    """
    Run the process extractor on a sample document.
    """

    extractor = ProcessExtractor(model="gpt-4.1-mini")

    input_file = "./test_data/Shakti AgroChem Industries Processes.pdf"

    processes = extractor.extract_processes(input_file)

    print(json.dumps(processes, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()

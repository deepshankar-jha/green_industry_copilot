from process_extractor import ProcessExtractor
from dotenv import load_dotenv
load_dotenv()

extractor = ProcessExtractor(
    model="gpt-4o"
)

processes = extractor.extract_processes(
    "./test_data/Shakti AgroChem Industries Processes.pdf"
)

print(processes)
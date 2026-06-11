"""
===============================================================================
Process Extractor
===============================================================================

This module extracts industrial process information from text documents and
converts it into structured JSON using an OpenAI language model.

Supported input formats
-----------------------
- TXT
- Markdown (.md)
- Microsoft Word (.docx)
- PDF

The extracted output follows a structured schema describing:

- Process metadata
- Inputs and outputs
- By-products
- Energy consumption
- Water usage
- Emissions
- Cost information
- Process dependencies

The OpenAI API key is automatically loaded from the
OPENAI_API_KEY environment variable.

Example
-------
extractor = ProcessExtractor()

processes = extractor.extract_processes("plant_processes.docx")

extractor.save_json(
    "plant_processes.docx",
    "processes.json"
)
===============================================================================
"""

from pathlib import Path
import json
from langchain_openai import ChatOpenAI
import docx
from pypdf import PdfReader
import os

from schemas import *
from dotenv import load_dotenv

load_dotenv()


class ProcessExtractor:
    """
    Extracts industrial process information from documents using OpenAI.

    Features
    --------
    - Supports TXT, MD, DOCX and PDF files.
    - Uses LangChain structured output.
    - Produces strongly typed JSON data.
    - Automatically loads the API key from the environment.

    Parameters
    ----------
    model : str
        OpenAI model to use for extraction.

    Raises
    ------
    ValueError
        If OPENAI_API_KEY is not defined.
    """

    def __init__(self):
        """
        Initialize the extractor and create the OpenAI client.

        Parameters
        ----------
        model : str
            OpenAI model name.

        Raises
        ------
        ValueError
            If OPENAI_API_KEY is not available.
        """
        self.llm = ChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=0,
            max_completion_tokens=30000,
        )

    ###############################################################################
    # File Readers
    #
    # These helper functions convert various document formats into plain text.
    # All extracted text is later supplied to the language model.
    ###############################################################################

    def _load_txt(self, filepath: str) -> str:
        """
        Read a text file.

        Parameters
        ----------
        filepath : str
            Path to the .txt file.

        Returns
        -------
        str
            File contents.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _load_md(self, filepath: str) -> str:
        """
        Read a markdown file and return its contents.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _load_docx(self, filepath: str) -> str:
        """
        Extract all paragraph text from a Word document.

        Parameters
        ----------
        filepath : str
            Path to the DOCX file.

        Returns
        -------
        str
            Combined document text.
        """
        doc = docx.Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])

    def _load_pdf(self, filepath: str) -> str:
        """
        Extract text from every page of a PDF document.

        Parameters
        ----------
        filepath : str
            Path to the PDF file.

        Returns
        -------
        str
            Concatenated page contents.
        """
        reader = PdfReader(filepath)

        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        return "\n".join(pages)

    ###############################################################################
    # Document Loader
    #
    # Determines the file type and dispatches loading to the appropriate reader.
    ###############################################################################

    def load_file(self, filepath: str) -> str:
        """
        Load text from a supported document.

        Supported formats
        -----------------
        - .txt
        - .md
        - .docx
        - .pdf

        Parameters
        ----------
        filepath : str
            Input document path.

        Returns
        -------
        str
            Extracted text.

        Raises
        ------
        ValueError
            If the file extension is unsupported.
        """

        suffix = Path(filepath).suffix.lower()

        loaders = {
            ".txt": self._load_txt,
            ".md": self._load_md,
            ".docx": self._load_docx,
            ".pdf": self._load_pdf,
        }

        if suffix not in loaders:
            raise ValueError(f"Unsupported format: {suffix}")

        return loaders[suffix](filepath)

    ###############################################################################
    # Process Extraction
    #
    # Converts raw document text into structured process information using
    # LangChain structured output and Pydantic schemas.
    ###############################################################################
    def extract_processes(self, filepath: str):
        """
        Extract industrial process steps from a document.

        The document is first converted to text and then passed to the
        language model. The model returns data that conforms to the
        ProcessList schema.

        Parameters
        ----------
        filepath : str
            Input document path.

        Returns
        -------
        list[dict]
            List of extracted process dictionaries.
        """

        document_text = self.load_file(filepath)

        prompt = f"""Rewrite the following industrial document into a normalized plain-text form and extract all industrial processes.

Requirements for document normalization:

* Preserve ALL information.
* Preserve process ordering.
* Preserve process names exactly.
* Do not summarize.
* Do not add information.
* Use ASCII characters only.
* Replace superscripts with ^ notation.

Examples:

m³/day -> m^3/day
m² -> m^2
CO₂ -> CO2

For money:

₹7,50,000/day -> INR 750000/day
$1800/hour -> USD 1800/hour

* Preserve section headings and process numbering.
* Return plain text only for the normalized document.

Process extraction rules:

* Extract all industrial processes from the document.
* Preserve process ordering.
* Preserve process names exactly as they appear in the normalized document.
* Process names must be unique.
* Never invent processes.
* next_processes must contain process names, never IDs.
* Every entry inside next_processes must exactly match the process_name of another extracted process.
* Do not use abbreviations, aliases, or modified names in next_processes.
* If a referenced downstream process does not exist among the extracted processes, use an empty list instead.
* Use null for missing scalar values.
* Use [] for missing lists.
* Preserve all numerical values and units exactly.

Validation rules:

* Each process_name must be unique.
* Every value appearing in next_processes must be an exact string match to an existing process_name.
* next_processes must contain only valid process names from the extracted process list.
* If there is any ambiguity about the downstream process name, use [] instead of guessing.
* Never create or infer process names that are not explicitly present in the document.

Document:

{document_text}
"""

        structured_llm = self.llm.with_structured_output(ProcessList)

        result = structured_llm.invoke(prompt)

        processes = [p.model_dump() for p in result.processes]

        return processes

    ###############################################################################
    # Export Utilities
    #
    # Functions for writing extracted process data to external files.
    ###############################################################################

    def save_json(self, filepath: str, output_path: str):
        """
        Extract process information and save it as a JSON file.

        Parameters
        ----------
        filepath : str
            Source document.

        output_path : str
            Destination JSON file.

        Returns
        -------
        list[dict]
            Extracted process data.
        """
        processes = self.extract_processes(filepath)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(processes, f, indent=4, ensure_ascii=False)

        return processes

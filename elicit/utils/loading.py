"""Script containing functions for loading documents."""
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator, PDFResourceManager
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage
from pathlib import Path
from typing import List, Optional, Union
import logging
import warnings
import yaml
import re

logging.getLogger('pdfminer').setLevel(logging.ERROR)


def load_pdf(path: Path, pages: Optional[List[int]] = None) -> str:
    """
    Load a PDF file into a string.

    :param path: Path to the PDF file.
    :param pages: List of pages to extract.
    """
    document = open(str(path.resolve()), "rb")
    # Create resource manager
    rsrcmgr = PDFResourceManager()
    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    doc: str = ""
    for page in PDFPage.get_pages(document, pagenos=pages):
        try:
            interpreter.process_page(page)
        except:
            warnings.warn(f"Could not process page {page.pageid}")
        # receive the LTPage object for the page.
        layout = device.get_result()
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                text = element.get_text()
                doc += text
    return doc


def load_document(document_location: Path, pdf_kwargs: dict = {}):
    """
    Load a document from a PDF or txt file.

    :param document_location: Path to the document.
    :param pdf_kwargs: Keyword arguments to pass to pdf_to_plaintext.

    :return: Document as a string.
    """
    if document_location.suffix == ".pdf":
        return pdf_to_plaintext(document_location, **pdf_kwargs)
    elif document_location.suffix == ".txt":
        with open(document_location, "r") as f:
            text = f.read()
            text = re.sub("[^a-zA-Z0-9'., ]+", ' ', text)
            return text
    else:
        raise ValueError(f"Unknown file type {document_location.suffix}")


def pdf_to_plaintext(pdf_location: Path, pages: Optional[List[int]] = None, newlines: bool = False, raw: bool = False) -> str:
    """
    Load a PDF file into a string. Contains some minor post-processing.

    :param pdf_location: Path to the PDF file.
    :param pages: List of pages to extract.
    :param newlines: Whether to replace newlines with spaces.
    :param raw: Whether to return the raw text.

    :return: pdf in plaintext.
    """
    raw_text = load_pdf(pdf_location, pages=pages)
    if not raw:
        raw_text = raw_text.replace("\xa0", " ")
        raw_text = raw_text.replace("\x0c", "")
        if not newlines:
            raw_text = raw_text.replace("\n", " ")
    return raw_text


def load_schema(schema_path: Path) -> dict[str, Union[str, List[str]]]:
    """
    Load a schema from a YAML file.

    :param schema_path: Path to the YAML file.

    :return: Schema as a dictionary.
    """
    with open(schema_path, "r") as f:
        return yaml.safe_load(f)

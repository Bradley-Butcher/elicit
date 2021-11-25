import pandas as pd
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator, PDFResourceManager
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage
from prefect import task
from pathlib import Path
from io import StringIO
from typing import List, Optional
import logging
import warnings

logging.getLogger('pdfminer').setLevel(logging.ERROR)


def load_pdf(path: Path, pages: Optional[List[int]] = None) -> str:
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


def _filter_list(l: list) -> list:
    return [x.replace("\n", " ") for x in l]


def load_offense_list() -> List[str]:
    """
    Loads the list of offenses from the CSV file.
    """
    data_path = Path(__file__).parent.parent / 'data' / 'simple_offenses.csv'
    offenses = pd.read_csv(open(str(data_path.resolve()), errors='ignore'))
    return _filter_list(offenses['Offence'].tolist())


def load_instrument_list() -> List[str]:
    """
    Loads the list of instruments from the CSV file.
    """
    data_path = Path(__file__).parent.parent / 'data' / 'offenses.csv'
    offenses = pd.read_csv(open(str(data_path.resolve()), errors='ignore'))
    return _filter_list(offenses['Instrument'].tolist())

@task
def pdf_to_plaintext(pdf_location: Path, pages: Optional[List[int]] = None, newlines: bool = False, raw: bool = False) -> str:
    raw_text = load_pdf(pdf_location, pages=pages)
    if not raw:
        raw_text = raw_text.replace("\xa0", " ")
        raw_text = raw_text.replace("\x0c", "")
        if not newlines:
            raw_text = raw_text.replace("\n", "")
    return raw_text

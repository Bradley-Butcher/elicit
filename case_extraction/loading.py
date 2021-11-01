import pandas as pd
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pathlib import Path
from io import StringIO
from typing import List, Optional
import logging

logging.getLogger('pdfminer').setLevel(logging.ERROR)


def load_pdf(path: Path, pages: Optional[List[int]] = None) -> str:
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    if pages:
        pagenos = set(pages)

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def _filter_list(l: list) -> list:
    return [x.replace("\n", " ") for x in l]


def load_offense_list() -> List[str]:
    """
    Loads the list of offenses from the CSV file.
    """
    data_path = Path(__file__).parent.parent / 'data' / 'offenses.csv'
    offenses = pd.read_csv(open(str(data_path.resolve()), errors='ignore'))
    return _filter_list(offenses['Offence'].tolist())


def load_instrument_list() -> List[str]:
    """
    Loads the list of instruments from the CSV file.
    """
    data_path = Path(__file__).parent.parent / 'data' / 'offenses.csv'
    offenses = pd.read_csv(open(str(data_path.resolve()), errors='ignore'))
    return _filter_list(offenses['Instrument'].tolist())


def pdf_to_plaintext(pdf_location: Path, pages: Optional[List[int]] = None, raw: bool = False) -> str:
    raw_text = load_pdf(pdf_location, pages=pages)
    if not raw:
        raw_text = raw_text.replace("\xa0", "")
        raw_text = raw_text.replace("\x0c", "")
    return raw_text

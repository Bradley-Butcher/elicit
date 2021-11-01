from pathlib import Path

from case_extraction.loading import pdf_to_plaintext
from case_extraction.extraction import extract_type

from tqdm import tqdm

pdf_path = Path(__file__).parent.parent / 'pdfs'


def count_scans(pdf_path: Path) -> int:
    """
    Count the number of scans in a folder of PDFs.
    """
    count = 0
    pdfs = list(pdf_path.glob('*.pdf'))
    for pdf in tqdm(pdfs, desc='Counting PDFs', total=len(pdfs)):
        text = pdf_to_plaintext(pdf)
        if text == '':
            count += 1
    return count


if __name__ == '__main__':
    print(f"Number of scans: {count_scans(pdf_path)}")

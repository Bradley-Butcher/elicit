"""Judicary website meta-data is not complete. This script updates extracted metadata fields by looking at filenames/text."""
from case_extraction.case import is_remarks, is_appeal
from case_extraction.load import pdf_to_plaintext
from pathlib import Path

import pandas as pd
from tqdm import tqdm

pdf_path = Path(__file__).parent.parent / 'pdfs'


def update_metadata(metadata_df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the sentencing remarks in the metadata.
    """
    pdfs = list(pdf_path.glob('*.pdf'))
    for pdf in tqdm(pdfs, desc='Counting PDFs', total=len(pdfs)):
        pdf_text = pdf_to_plaintext(pdf, pages=[0])
        if is_remarks(pdf_text, pdf.stem):
            metadata_df.loc[metadata_df["Case Name"] ==
                            str(pdf.stem).replace("_", " "), 'Sentencing Remarks'] = 1
        if is_appeal(pdf_text, pdf.stem):
            metadata_df.loc[metadata_df["Case Name"] ==
                            str(pdf.stem).replace("_", " "), 'Court of Appeal'] = 1
    return metadata_df


if __name__ == '__main__':
    metadata_df = pd.read_csv(pdf_path / 'crime_metadata.csv')
    metadata_df = update_metadata(metadata_df)
    metadata_df.to_csv(pdf_path / 'crime_metadata.csv', index=False)

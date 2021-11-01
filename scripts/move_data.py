"""This script moves data in folders based on whether they're: crown court / court of appeal / other."""
from pathlib import Path
import shutil

import pandas as pd
from tqdm import tqdm


def _get_fromto_tuple(df: pd.DataFrame, base_dir: Path) -> list:
    df["Case Name"] = df["Case Name"].apply(
        lambda x: f"{x.replace(' ', '_').replace('/', '')}.pdf")
    return [(base_dir / fr, base_dir / to) for fr, to in zip(df["Case Name"], df["location"])]


def move_data(pdf_dir: Path) -> None:
    metadata_df = pd.read_csv(pdf_dir / "crime_metadata.csv")
    metadata_df["location"] = "other"
    metadata_df.loc[(metadata_df["Crown Court"] == 1) & (
        metadata_df["Court of Appeal"] == 0), "location"] = "crown court"
    court_of_appeal = metadata_df.loc[(metadata_df["Crown Court"] == 0) & (
        metadata_df["Court of Appeal"] == 1), "location"] = "court of appeal"
    (pdf_dir / "other").mkdir(exist_ok=True)
    (pdf_dir / "crown court").mkdir(exist_ok=True)
    (pdf_dir / "court of appeal").mkdir(exist_ok=True)
    for fr, to in tqdm(_get_fromto_tuple(metadata_df, pdf_dir), desc="Moving data"):
        try:
            shutil.move(str(fr.resolve()), str(to.resolve()))
        except:
            continue


if __name__ == '__main__':
    pdf_path = Path(__file__).parent.parent / 'pdfs'
    move_data(pdf_path)

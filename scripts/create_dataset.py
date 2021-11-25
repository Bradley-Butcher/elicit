"""This script injests PDFs and creates txt training/test datasets."""
from pathlib import Path
import random
from typing import List
import argparse

from case_extraction.loading import pdf_to_plaintext
from case_extraction.example_cases import load_test_cases

import pandas as pd
from tqdm import tqdm

pdf_dir = Path(__file__).parent.parent / "pdfs"


def save_txt_files(txts: List[str], save_location: Path) -> None:
    save_location.mkdir(exist_ok=True)
    for i, txt in tqdm(enumerate(txts), total=len(txts), desc="Saving TXT files"):
        with open(save_location / f"{i}.txt", "w") as f:
            f.write(txt)


def create_record(court: str, train_filenames: List[str], test_filenames: List[str]) -> pd.DataFrame:
    train_df = pd.DataFrame([{"pdf_filename": f"{court}/{fn}", "data_filename": f"train/{i}.txt"}
                            for i, fn in enumerate(train_filenames)])
    test_df = pd.DataFrame([{"pdf_filename": f"{court}/{fn}", "data_filename": f"test/{i}.txt"}
                            for i, fn in enumerate(test_filenames)])
    return pd.concat([train_df, test_df])


def create_train_test_dataset(court: str, output_dir: Path, n_train_samples: int, n_test_samples: int, seed: int = 1) -> None:
    court_dir = pdf_dir / court
    random.seed(seed)
    assert n_train_samples + \
        n_test_samples <= len(list(court_dir.glob("*.pdf"))
                              ), "Not enough PDFs in the directory"
    docs = sorted(set([case.name for case in court_dir.glob(
        "*.pdf")]) - set([case.filename for case in load_test_cases()]))
    random.shuffle(docs)
    print("------ Converting PDFs to TXT -----------")
    print(" TRAINING: ")
    training_pdf = []
    for d in tqdm(docs[:n_train_samples], desc="Converting Training PDFs to TXT", total=n_train_samples):
        training_pdf.append(pdf_to_plaintext(court_dir / d, newlines=False))
    test_pdfs = []
    print(" TESTING: ")
    for d in tqdm(docs[-n_test_samples:], desc="Converting Test PDFs to TXT", total=n_test_samples):
        test_pdfs.append(pdf_to_plaintext(court_dir / d, newlines=False))
    print("------ Saving TXT files -----------")
    print(" TRAINING: ")
    save_txt_files(training_pdf, output_dir / "train")
    print(" TESTING: ")
    save_txt_files(test_pdfs, output_dir / "test")
    record_df = create_record(
        court, docs[:n_train_samples], docs[-n_test_samples:])
    record_df.to_csv(output_dir / "record.csv", index=False)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--court", type=str, required=True)
    argparser.add_argument("--output_dir", type=str, required=True)
    argparser.add_argument("--n_train_samples", type=int, required=True)
    argparser.add_argument("--n_test_samples", type=int, required=True)
    argparser.add_argument("--seed", type=int, default=1)
    args = argparser.parse_args()
    create_train_test_dataset(args.court, Path(
        args.output_dir), args.n_train_samples, args.n_test_samples, args.seed)

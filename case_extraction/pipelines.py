from typing import Callable, List
from prefect import flow

from pathlib import Path
from prefect.flows import Flow
from case_extraction.case import Case

from case_extraction.components.nli_transformer import extract_variables
from case_extraction.components.defendants import get_defendants
from case_extraction.components.sex import sex_from_name
from case_extraction.ensembler import Ensembler
from case_extraction.utils.loading import pdf_to_plaintext

@flow(name="transformer_flow")
def transformer_flow(doc: str, pdf: Path, question_schema: Path, categories_schema: Path):
    case = Case(filename=pdf.stem, method="transformer")
    case = get_defendants(filename=pdf, doc=doc, case=case)
    case = extract_variables(doc=doc, case=case, question_schema=question_schema, categories_schema=categories_schema)
    case = sex_from_name(case)
    return case


@flow
def main_flow(pdfs: List[Path], question_schema: Path, categories_schema: Path) -> List[Case]:
    cases: List[Case] = []
    for pdf in pdfs:
        doc = pdf_to_plaintext(pdf)
        case = transformer_flow(doc=doc, pdf=pdf, question_schema=question_schema, categories_schema=categories_schema)
        cases.append(case)
    return cases

def run_ensemble(flow: Callable, ensemble_mode: str, **kwargs: dict) -> List[Case]:
    output = flow(**kwargs)
    cases = get_cases_from_flow(flow=output)
    ensembler = Ensembler(mode = ensemble_mode)
    cases = ensembler.combine(cases)
    return cases


def get_cases_from_flow(flow: Flow) -> List[Case]:
    cases: List[Case] = []
    for result in flow.result():
        cases.append(result.result().result())
    return cases

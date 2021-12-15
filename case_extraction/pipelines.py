from typing import Callable, List
from prefect import flow

from pathlib import Path
from prefect.flows import Flow
from case_extraction.case import Case
from case_extraction.components.keyword_search import exact_match

from case_extraction.components.nli_transformer import nli_extraction
from case_extraction.components.similarity_transformer import sim_extraction
from case_extraction.components.defendants import get_defendants
from case_extraction.components.regex import get_defendants_regex, get_victims_regex
from case_extraction.ensembler import Ensembler
from case_extraction.utils.loading import pdf_to_plaintext

@flow(name="nli_flow")
def nli_flow(doc: str, pdf: Path, question_schema: Path, categories_schema: Path):
    case = Case(filename=pdf.stem, method="transformer_nli")
    case = get_defendants(filename=pdf, doc=doc, case=case)
    case = nli_extraction(doc=doc, case=case, question_schema=question_schema, categories_schema=categories_schema)
    return case

@flow(name="similarity_flow")
def sim_flow(doc: str, pdf: Path, question_schema: Path, categories_schema: Path):
    case = Case(filename=pdf.stem, method="transformer_sim")
    case = get_defendants(filename=pdf, doc=doc, case=case)
    case = sim_extraction(doc=doc, case=case, question_schema=question_schema, categories_schema=categories_schema)
    return case

@flow(name="regex_flow")
def regex_flow(doc: str, pdf: Path) -> Case:
    case = Case(filename=pdf.stem, method="regex")
    case = get_defendants_regex(doc, case)
    case = get_victims_regex(doc, case)
    return case

@flow(name="keyword_flow")
def keyword_flow(doc: str, pdf: Path, keyword_schema: Path) -> Case:
    case = Case(filename=pdf.stem, method="keyword")
    case = exact_match(doc, case, keyword_schema)
    return case

@flow(name="ipet_flow")
def ipet_flow(doc: str, pdf: Path, pattern_schema: Path, categories_schema: Path) -> List[Case]:
    case = Case(filename=pdf.stem, method="ipet")
    return case


@flow
def main_flow(pdfs: List[Path], question_schema: Path, categories_schema: Path, keyword_schema: Path) -> List[Case]:
    cases: List[Case] = []
    for pdf in pdfs:
        doc = pdf_to_plaintext(pdf)
        # sub-flows
        nli_case = nli_flow(doc=doc, pdf=pdf, question_schema=question_schema, categories_schema=categories_schema)
        sim_case = sim_flow(doc=doc, pdf=pdf, question_schema=question_schema, categories_schema=categories_schema)
        keyword_case = keyword_flow(doc=doc, pdf=pdf, keyword_schema=keyword_schema)
        # Append Cases
        cases += [nli_case, sim_case, keyword_case]
    return cases

def run_ensemble(flow: Callable, ensemble_args: dict, **kwargs: dict) -> List[Case]:
    output = flow(**kwargs)
    cases = get_cases_from_flow(flow=output)
    ensembler = Ensembler(**ensemble_args)
    cases = ensembler.combine(cases)
    return cases


def get_cases_from_flow(flow: Flow) -> List[Case]:
    cases: List[Case] = []
    for result in flow.result():
        cases.append(result.result().result())
    return cases

"""
Main pipeline launch-point. 
Currently uses prefect to chain functions together, this will be changed in a future release.

"""
from typing import Callable, List
from prefect import flow

from pathlib import Path
from prefect.flows import Flow
from elicit.case import Case
from elicit.components.keyword_search import exact_match

from elicit.components.nli_transformer import nli_extraction
from elicit.components.similarity_transformer import sim_extraction
from elicit.components.defendants import get_defendants
from elicit.components.regex import get_defendants_regex, get_victims_regex
from elicit.components.semantic_search import search
from elicit.vectorizer import Vectorizer
from elicit.utils.loading import pdf_to_plaintext

@flow(name="nli_flow")
def nli_flow(doc: str, pdf: Path, question_schema: Path, categories_schema: Path):
    case = Case(filename=pdf.stem, method="NLI Transformer")
    # case = get_defendants(filename=pdf, doc=doc, case=case)
    case = nli_extraction(doc=doc, case=case, question_schema=question_schema, categories_schema=categories_schema)
    return case

@flow(name="filename_flow")
def filename_flow(doc: str, pdf: Path):
    case = Case(filename=pdf.stem, method="filename_extractor")
    case = get_defendants(filename=pdf, doc=doc, case=case)
    return case

@flow(name="similarity_flow")
def sim_flow(doc: str, pdf: Path, question_schema: Path, categories_schema: Path):
    case = Case(filename=pdf.stem, method="Similarity Transformer")
    # case = get_defendants(filename=pdf, doc=doc, case=case)
    case = sim_extraction(doc=doc, case=case, question_schema=question_schema, categories_schema=categories_schema)
    return case

@flow(name="semantic_flow")
def semantic_flow(doc: str, pdf: Path, question_schema: Path, categories_schema: Path):
    case = Case(filename=pdf.stem, method="Semantic Search")
    # case = get_defendants(filename=pdf, doc=doc, case=case)
    case = search(doc=doc, case=case, question_schema=question_schema, categories_schema=categories_schema)
    return case

@flow(name="regex_flow")
def regex_flow(doc: str, pdf: Path) -> Case:
    case = Case(filename=pdf.stem, method="regex")
    case = get_defendants_regex(doc, case)
    case = get_victims_regex(doc, case)
    return case

@flow(name="keyword_flow")
def keyword_flow(doc: str, pdf: Path, keyword_schema: Path, categories_schema: Path) -> Case:
    case = Case(filename=pdf.stem, method="keyword")
    case = exact_match(doc, case, keyword_schema, categories_schema)
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
        keyword_case = keyword_flow(doc=doc, pdf=pdf, keyword_schema=keyword_schema, categories_schema=categories_schema)
        # filename_case = filename_flow(doc=doc, pdf=pdf)
        semantic_case = semantic_flow(doc=doc, pdf=pdf, question_schema=question_schema, categories_schema=categories_schema)
        # Append Cases
        cases += [nli_case, sim_case, keyword_case, semantic_case]
    return cases

def run_flow(flow: Callable, ensemble_args: dict, **kwargs: dict) -> None:
    output = flow(**kwargs)
    cases = get_cases_from_flow(flow=output)
    vectorizer = Vectorizer(**ensemble_args)
    cases = vectorizer.combine_and_store(cases)

def get_cases_from_flow(flow: Flow) -> List[Case]:
    cases: List[Case] = []
    for result in flow.result():
        cases.append(result.result().result())
    return cases

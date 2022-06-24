"""Script which uses a Natural Language Inference transfomer model assign extracted Q&A pairs to provided categories."""
import yaml
from transformers import Pipeline, pipeline
from pathlib import Path
from typing import DefaultDict, Dict, List, Tuple
import re
import warnings
from elicit.interface import CategoricalLabellingFunction, Extraction

from elicit.labelling_functions.qa_transformer import extract_answers


warnings.filterwarnings("ignore")


# def extract_value(answers: List[Tuple[str, float, int, int]], doc: str, threshold: float) -> Union[DocumentField, List[DocumentField]]:
#     """
#     Extract numerical value from the output Q&A Transformer, only used if variable category is assigned as "continuous".

#     :param answers: List of answers from Q&A Transformer.
#     :param doc: Document string.
#     :param threshold: Threshold for the Q&A Transformer. Only answers above this threshold are considered.

#     :return: Either CaseField object with the extracted value, or a list of CaseField objects with the extracted values. Depending on the number of valid answers.
#     """
#     values = [(re.findall(r'\d+', answer)[0], score, start, end)
#               for answer, score, start, end in answers if score > threshold and re.findall(r'\d+', answer)]
#     if not values:
#         return DocumentField(value="unknown", confidence=0, evidence=Extraction.abstain())
#     values, context = compress(values)
#     output = [DocumentField(value=k, confidence=v, evidence=Extraction.from_character_startend(
#         doc, context[k]["start"], context[k]["end"])) for k, v in values.items()]
#     if len(output) == 1:
#         return output[0]
#     return output


def compress(candidates: List[Tuple[str, float, int, int]]) -> Dict[str, float]:
    """
    Compress the list of candidate answers, summing the probabilities where the answer is the same.
    Context returned is the max of the same answer.

    :param candidates: List of candidate answers. Form is [(answer, score, start, end)]. Multiple answers can be the same, but coming from different parts of the document. These are summed together.

    :return: Dictionary of answers and their probabilities.
    """
    prob_dict = DefaultDict(float)
    prob_sum = 0.0
    max_context = {}
    max_candidate = DefaultDict(float)
    for candidate, prob, start, end in candidates:
        if prob > max_candidate[candidate]:
            max_candidate[candidate] = prob
            max_context[candidate] = {"start": start, "end": end}
    for ci in candidates:
        prob_dict[ci[0]] += ci[1]
        prob_sum += ci[1]
    return {k: v / prob_sum for k, v in prob_dict.items()}, max_context


def match_classify(answers: List[Tuple[str, float]], document_text: str, levels: List[str], classification_model: Pipeline, filter_threshold: float, threshold: float) -> Tuple[str, float]:
    """
    Match answers from the Q&A Transformer to the levels of the variable.

    :param answers: List of answers from Q&A Transformer.
    :param doc: Document string.
    :param levels: List of levels for the variable.
    :param threshold: Threshold for the Q&A Transformer. Only answers above this threshold are considered.

    :return: Tuple of the matched level and the confidence of the match.
    """
    candidates = []
    for answer, score, start, end in answers:
        if answer in levels:
            candidates.append((answer, score, start, end))
        else:
            output = classification_model(
                answer,
                [*levels, ""],
                multi_label=True
            )
            candidates += [(output["labels"][i], output["scores"][i] * score, start, end)
                           for i in range(len(output["labels"])) if output["scores"][i] > filter_threshold]
    if not candidates:
        return [Extraction.abstain()]
    compressed_candidates, context = compress(candidates)
    candidates = [(o, s)
                  for o, s in compressed_candidates.items() if s > threshold]

    # create a list of Extraction for each candidate
    extractions = []
    for candidate, score in candidates:
        if candidate == "":
            continue
        extractions.append(Extraction.from_character_startend(
            document_text,
            candidate,
            score,
            context[candidate]["start"],
            context[candidate]["end"]
        ))

    if len(extractions) == 0:
        return [Extraction.abstain()]
    else:
        return extractions


# def extract_top(answers: List[Tuple[str, float, int, int]], doc: str) -> List[DocumentField]:
#     """
#     Extract top answer from Q&A Transformer. This is used if variable category is assigned as "raw".

#     :param answers: List of answers from Q&A Transformer.
#     :param doc: Document string.

#     :return: List of CaseField objects with the extracted values.
#     """
#     if not answers:
#         return DocumentField(value="unknown", confidence=0, evidence=Extraction.abstain())
#     answers, context = compress(answers)
#     return [DocumentField(value=k, confidence=v, evidence=Extraction.from_character_startend(doc, context[k]["start"], context[k]["end"])) for k, v in answers.items()]


# def process_answers(answers: Dict[str, Tuple[str, float, int, int]], doc: str, categories_schema: Path, threshold: float = 0.7) -> Dict[str, List[str]]:
#     """
#     Process the answers from the Q&A Transformer.
#     Assigns Categorical variables to provided categories, extracts numerical values for continuous variables, and extracts top answers for raw variables.

#     :param answers: Dictionary of answers from Q&A Transformer.
#     :param doc: Document string.
#     :param categories_schema: Path to the categories schema.
#     :param threshold: Threshold for the Q&A Transformer. Only answers above this threshold are considered.

#     :return: Dictionary of answers and their values.
#     """
#     variables = load_schema(categories_schema)
#     extracted_variables = {}
#     for key in variables.keys():
#         if variables[key] == "continuous":
#             extracted_variables[key] = extract_value(
#                 answers=answers[key], doc=doc, threshold=threshold)
#         elif variables[key] == "raw":
#             extracted_variables[key] = extract_top(
#                 answers=answers[key], doc=doc)
#         else:
#             extracted_variables[key] = match_classify(
#                 answers=answers[key], doc=doc, levels=variables[key], threshold=threshold)
#     return extracted_variables


# @labelling_function(labelling_method="NLI Transformer", required_schemas=["question_schema", "categories_schema"])
# def nli_extraction(
#     doc: str,
#     document: Document,
#     question_schema: Path,
#     categories_schema: Path,
#     match_threshold: float = 0.3,
#     qa_threshold: float = 0.5,
#     device=None
# ) -> Document:
#     """
#     Task for using NLI to extract variables from a document.

#     :param doc: Document string.
#     :param case: Case object to add extracted variables to.
#     :param question_schema: Path to the question schema.
#     :param categories_schema: Path to the categories schema.
#     :param match_threshold: Threshold for the NLI Transformer. Only answers above this threshold are considered.
#     :param qa_threshold: Threshold for the Q&A Transformer. Only answers above this threshold are considered.

#     :return: Case object with extracted variables.
#     """
#     answers = extract_answers(
#         doc=doc, case=document, question_schema=question_schema, threshold=qa_threshold)
#     answer_dict = process_answers(
#         answers, doc=doc, categories_schema=categories_schema, threshold=match_threshold)
#     document.add_dict(answer_dict)
#     return document

class NLILabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)
        self.match_threshold = 0.5
        self.qna_threshold = 0.3

    def load(self) -> None:
        self.classifier = pipeline("zero-shot-classification",
                                   model="facebook/bart-large-mnli", device=0)
        self.qna_model = pipeline(
            'question-answering',
            model="deepset/roberta-base-squad2",
            tokenizer="deepset/roberta-base-squad2", device=0
        )

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)
        final_threshold = 1 / (len(categories) + 1)
        answers = extract_answers(
            document_text,
            questions=questions,
            qna_model=self.qna_model,
            threshold=self.qna_threshold
        )
        extractions = match_classify(
            answers=answers,
            document_text=document_text,
            levels=categories,
            classification_model=self.classifier,
            filter_threshold=self.match_threshold,
            threshold=final_threshold)
        self.push_many(document_name, variable_name, extractions)

    def train(self, document_name: str, variable_name: str, extraction: Extraction):
        pass

    @property
    def labelling_method(self) -> str:
        return "Q&A → NLI Transformer"

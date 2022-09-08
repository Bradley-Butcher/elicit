"""Script which uses a Natural Language Inference transfomer model assign extracted Q&A pairs to provided categories."""
import torch
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss, MSELoss

from transformers import AutoTokenizer, pipeline
from transformers import BartForSequenceClassification, BartTokenizerFast

from pathlib import Path
from typing import DefaultDict, Dict, List, Optional, Tuple, Union
import warnings

from elicit.interface import CategoricalLabellingFunction, Extraction


warnings.filterwarnings("ignore")


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
    candidates = [(cat, sc, st, end)
                  for cat, sc, st, end in candidates if sc > threshold]

    # create a list of Extraction for each candidate
    extractions = []
    for cat, sc, st, end in candidates:
        if cat == "":
            continue
        extractions.append(Extraction.from_character_startend(
            document_text,
            cat,
            sc,
            st,
            end
        ))

    if len(extractions) == 0:
        return [Extraction.abstain()]
    else:
        return extractions


def load_llm_model(model_directory: str):
    tokenizer = AutoTokenizer.from_pretrained(
        "impira/layoutlm-document-qa",
        add_prefix_space=True,
    )
    pipeline = pipeline(
        model="impira/layoutlm-document-qa",
        tokenizer=tokenizer,
        trust_remote_code=True,
    )
    return pipeline


def load_seq_model(model_directory: str) -> tuple[RobertaForQuestionAnsweringWithNegatives, BartTokenizerFast]:
    if (model_directory / "seq_model").exists():
        print("Fine tuned Sequence Classifier model found, loading...")
        tokenizer = BartTokenizerFast.from_pretrained(
            "facebook/bart-large-mnli")
        model = BartForSequenceClassificationWithNegatives.from_pretrained(
            model_directory / "seq_model")
    else:
        print("No fine tuned Sequence Classifier model found, loading generic model...")
        tokenizer = BartTokenizerFast.from_pretrained(
            "facebook/bart-large-mnli")
        model = BartForSequenceClassificationWithNegatives.from_pretrained(
            "facebook/bart-large-mnli")
    return model, tokenizer


class LayoutLMLabellingFunction(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)

    def load(self, model_directory: Path, device: Union[int, str]) -> None:
        self.device = device
        self.model_directory = model_directory
        self.vqa_model = load_llm_model(model_directory)
        self.seq_model, self.seq_tokenizer = load_seq_model(model_directory)
        self.classifier = pipeline(
            task='zero-shot-classification',
            model=self.seq_model,
            tokenizer=self.seq_tokenizer,
            device=device
        )

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)

    def train(self, data: dict[str, List["Extraction"]]):
        pass

    @property
    def labelling_method(self) -> str:
        return "Q&A → NLI Transformer"

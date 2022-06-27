"""Script which uses a masked transformer model."""

from pathlib import Path
from typing import List

from transformers import pipeline

from elicit.interface import CategoricalLabellingFunction

from elicit.utils.utils import split_doc

unmasker = pipeline('fill-mask', model='bert-base-uncased')

def mask_variable(doc: str, masks: List[str], threshold: float = 0.3) -> List[DocumentField]:
    weighted_dict = {}
    evidence_dict = {}
    max_dict = {}
    norm = 0
    for mask in masks:
        mask_length = len(mask)
        for sentence in split_doc(doc, max_length= 512 - (mask_length + 1)):
            norm += 1
            sentence = sentence + " " + mask
            unmasker_output = unmasker(sentence)
            for output in unmasker_output:
                if output["score"] < threshold:
                    continue
                weighted_dict[output["token_str"]] = weighted_dict.get(output["token_str"], 0) + output["score"]
                # norm_dict[output["token_str"]] = norm_dict.get(output["token_str"], 0) + 1
                if max_dict.get(output["token_str"], 0) < output["score"]:
                    max_dict[output["token_str"]] = output["score"]
                evidence_dict[output["token_str"]] = sentence
    weighted_dict = {key: value / norm for key, value in weighted_dict.items()}
    return weighted_dict, evidence_dict

def topk_keys(weighted_dict: dict, topk: int = 3) -> List[str]:
    """
    Return the topk keys of a dictionary sorted by value.

    """
    return [key for key, value in sorted(weighted_dict.items(), key=lambda item: item[1], reverse=True)][:topk]

def categorical_mask(doc: str, masks: List[str], levels: List[str], topk: int = 10):
    weighted_dict, evidence_dict = mask_variable(doc, masks["prompts"])
    fields = []
    for key in topk_keys(weighted_dict, topk):
        evidence = evidence_dict[key].replace("[MASK]", key)
        if masks["type"] == "boolean":
            # if key.lower() in ["was", "is"]:
            #     fields += [DocumentField(levels[0], weighted_dict[key], Evidence.from_string(evidence))]
            continue
        if masks["type"] == "direct":
            if key in levels:
                fields += [DocumentField(key, weighted_dict[key], Extraction.from_string(evidence))]
    return fields

def continuous_mask(doc: str, masks: List[str], topk: int = 10):
    weighted_dict, evidence_dict = mask_variable(doc, masks["prompts"])
    fields = []
    for key in topk_keys(weighted_dict, topk):
        evidence = evidence_dict[key].replace("[MASK]", key)
        if key.isnumeric():
            fields += [DocumentField(key, weighted_dict[key], Extraction.from_string(evidence))]
    return fields

def raw_mask(doc: str, masks: List[str], topk: int = 3, threshold: float = 0.3):
    weighted_dict, evidence_dict = mask_variable(doc, masks["prompts"])
    fields = []
    for key in topk_keys(weighted_dict, topk):
        evidence = evidence_dict[key].replace("[MASK]", key)
        if weighted_dict[key] > threshold:
            fields += [DocumentField(key, weighted_dict[key], Extraction.from_string(evidence))]
    return fields


@labelling_function(labelling_method="Mask Transformer", required_schemas=["mask_schema", "categories_schema"])
def mask_extraction(
    doc: str, 
    document: Document,
    mask_schema: Path, 
    categories_schema: Path, 
) -> Document:
    masks = load_schema(mask_schema)
    categories = load_schema(categories_schema)
    for variable in categories.keys():
        if categories[variable] == "continuous":
            cfs = continuous_mask(doc, masks[variable])
        elif categories[variable] == "raw":
            cfs = raw_mask(doc, masks[variable])
        else:
            cfs = categorical_mask(doc, masks[variable], categories[variable])
        document.add_fields(variable, cfs)
    return document

class MaskTransformerLF(CategoricalLabellingFunction):
    def __init__(self, schemas, logger, **kwargs):
        super().__init__(schemas, logger, **kwargs)
        self.sim_threshold = 0.25
    
    def load(self) -> None:
        self.model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1', device="cuda")

    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        questions = self.get_schema("questions", variable_name)
        categories = self.get_schema("categories", variable_name)
        doc_sims = doc_similarities(questions, document_text, self.model)
        matched_level, matched_sentence, matched_score = match_levels(doc_sims, categories, self.model, self.sim_threshold)
        if matched_level:
            s_start, s_end = get_sentence_start_end(document_text, matched_sentence)
            self.push(document_name, variable_name, Extraction.from_character_startend(document_text, matched_level, matched_score, s_start, s_end))

    def train(self, document_name: str, variable_name: str, extraction: Extraction):
        pass

    @property
    def labelling_method(self) -> str:
        return "Semantic Search"





            
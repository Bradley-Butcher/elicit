"""Script which uses a masked transformer model."""

from pathlib import Path
from typing import List

from transformers import pipeline

from elicit.document import Document, DocumentField, Evidence
from elicit.pipeline import labelling_function
from elicit.utils.loading import load_schema

unmasker = pipeline('fill-mask', model='bert-base-uncased')

def split_doc(doc: str, max_length: int = 512, token: str = ".") -> list:
    """Split a document into sentences. 
    Splitting on the last period <Token> before the max length.

    Args:
        doc (str): Document to split.
        max_length (int): Maximum length of each sentence.

    Returns:
        list: List of sentences.
    """
    sections = []
    current_end = 0
    while current_end <= len(doc):
        if current_end + max_length >= len(doc):
            sections.append(doc[current_end:])
            break
        section_end = doc[current_end:current_end + max_length].rfind(token) + current_end
        sections += [doc[current_end:section_end]]
        current_end = section_end
    return sections

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
                fields += [DocumentField(key, weighted_dict[key], Evidence.from_string(evidence))]
    return fields

def continuous_mask(doc: str, masks: List[str], topk: int = 10):
    weighted_dict, evidence_dict = mask_variable(doc, masks["prompts"])
    fields = []
    for key in topk_keys(weighted_dict, topk):
        evidence = evidence_dict[key].replace("[MASK]", key)
        if key.isnumeric():
            fields += [DocumentField(key, weighted_dict[key], Evidence.from_string(evidence))]
    return fields

def raw_mask(doc: str, masks: List[str], topk: int = 3, threshold: float = 0.3):
    weighted_dict, evidence_dict = mask_variable(doc, masks["prompts"])
    fields = []
    for key in topk_keys(weighted_dict, topk):
        evidence = evidence_dict[key].replace("[MASK]", key)
        if weighted_dict[key] > threshold:
            fields += [DocumentField(key, weighted_dict[key], Evidence.from_string(evidence))]
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





            
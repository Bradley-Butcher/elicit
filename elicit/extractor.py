"""
Main extraction launch-point. 
Controlls document execution through registered labelling functions.

"""
import functools
from typing import Callable, List, Optional, Set, Type, Union

from pathlib import Path
from unittest.util import strclass

import yaml
from elicit.interface import ElicitLogger, Extraction, LabellingFunctionBase

from elicit.utils.loading import load_document

from tqdm import tqdm


class Extractor:
    def __init__(self, db_path: Path, model_path: Path = Path(__file__).parent / "models", device: int = -1, top_k: int = -1):
        self.logger = ElicitLogger(db_path)
        self.model_path = model_path
        model_path.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.lfs = []
        self.schemas = {}
        self.top_k = top_k

    def register_schema(self, schema: Union[Path, dict], schema_name: str) -> None:
        if len(self.lfs) > 0:
            raise ValueError(
                "Must register schemas before registering labelling functions.")
        if isinstance(schema, Path):
            with open(schema, "r") as f:
                self.schemas[schema_name] = yaml.safe_load(f)
        elif isinstance(schema, dict):
            self.schemas[schema_name] = schema
        print(f"Registered schema: {schema_name}")

    def register_labelling_function(self, labelling_function: Type[LabellingFunctionBase], function_kwargs: dict = {}) -> None:
        # could change to not initialize until run to avoid the loading order issue
        assert issubclass(
            labelling_function, LabellingFunctionBase), "Labelling function must be a subclass of LabellingFunctionBase."
        if self.schemas == {}:
            raise ValueError(
                "Must register schemas before registering labelling functions.")
        obj = labelling_function(schemas=self.schemas,
                                 logger=self.logger,
                                 top_k=self.top_k,
                                 **function_kwargs)
        self.lfs.append(obj)
        print(f"Registered labelling function: {obj.labelling_method}")

    @property
    def variables(self) -> List[str]:
        """Get list of variables from the categories schema, ValueError if category schema isn't loaded."""
        if not "categories" in self.schemas:
            raise ValueError(
                "'categories' schema yet to be registered. Cannot collect variables.")
        return list(self.schemas["categories"].keys())

    def _prepare_db(self, documents) -> None:
        for doc in documents:
            if self.logger.doc_in(doc.stem):
                continue
            for variable in self.variables:
                for value in self.schemas["categories"][variable]:
                    self.logger.push_variable(doc.stem, variable, value)
                self.logger.push_variable(doc.stem, variable, "ABSTAIN")

    def _var_type(self, variable: str) -> str:
        var_schema = self.schemas["categories"][variable]
        return var_schema if not isinstance(var_schema, list) else "categorical"

    def run(self, documents: List[Path]) -> None:
        """
        Run all labelling functions on the given documents.

        :param documents: List of paths to documents to be labelled.

        :return: None
        """
        self._prepare_db(documents)

        lf_obj: Type[LabellingFunctionBase]
        for lf_obj in self.lfs:
            print(f"Running LF: {lf_obj.labelling_method}")
            print("Loading Resources.")
            lf_obj.load(self.model_path, self.device)
            pbar = tqdm(documents)
            for doc in pbar:
                text = load_document(doc)
                for variable in self.variables:
                    if not lf_obj.type == self._var_type(variable):
                        continue
                    pbar.set_description(
                        f"Extracting variable: {variable}")
                    lf_obj.extract(doc.stem, variable, text)
            # free up memory from models and stuff
            del lf_obj

    def get_validated_documents(self, variable: str, include_negatives: bool) -> List[Path]:
        document_names = self.logger.get_validated_document_names(
            variable, include_negatives)
        print(
            f"{len(document_names)} documents with validations for variable: {variable}")
        return document_names

    def get_extractions(self, document_names: List[str], variable: str, include_negatives: bool) -> List[Extraction]:
        extractions = self.logger.get_validated_extractions(
            document_names, variable, include_negatives)
        return extractions

    def train(self, include_negatives: bool = False) -> None:
        lf_obj: Type[LabellingFunctionBase]
        for lf_obj in self.lfs:
            if not lf_obj.loaded:
                print(f"Loading Resources for LF: {lf_obj.labelling_method}")
                lf_obj.load(self.model_path, self.device)
            data = {}
            for variable in self.variables:
                print(
                    f"Training LF: {lf_obj.labelling_method} on variable: {variable}")
                if not lf_obj.type == self._var_type(variable):
                    continue
                validated_documents = self.get_validated_documents(
                    variable, include_negatives)
                extraction_set = self.get_extractions(
                    validated_documents, variable, include_negatives)
                if len(extraction_set) == 0:
                    print(
                        f"No extractions for variable: {variable}")
                    continue
                else:
                    data[variable] = extraction_set
            lf_obj.train(data)

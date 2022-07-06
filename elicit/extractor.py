"""
Main extraction launch-point. 
Controlls document execution through registered labelling functions.

"""
import functools
from typing import Callable, List, Optional, Set, Type, Union

from pathlib import Path

import yaml
from elicit.interface import ElicitLogger, Extraction, LabellingFunctionBase

from elicit.utils.loading import load_document

from tqdm import tqdm


class Extractor:
    def __init__(self, db_path: Path):
        self.logger = ElicitLogger(db_path)
        self.lfs = []
        self.schemas = {}

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
                                 logger=self.logger, **function_kwargs)
        self.lfs.append(obj)
        print(f"Registered labelling function: {obj.labelling_method}")

    def _handle_loading(self):
        print("Handling LF loading")
        for lf_obj in self.lfs:
            print(f"Loading LF: {lf_obj.labelling_method}")
            lf_obj.load()

    @property
    def variables(self) -> List[str]:
        """Get list of variables from the categories schema, ValueError if category schema isn't loaded."""
        if not "categories" in self.schemas:
            raise ValueError(
                "'categories' schema yet to be registered. Cannot collect variables.")
        return list(self.schemas["categories"].keys())

    def _prepare_db(self, documents) -> None:
        for doc in documents:
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
            print("Loading models and stuff...")
            lf_obj.load()
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

"""
Main controller launch-point. 

"""
import functools
from typing import Callable, List, Optional, Set, Type

from pathlib import Path
from elicit.document import Document
from elicit.interface import ElicitLogger, LabellingFunctionBase


from elicit.vectorizer import Vectorizer
from elicit.utils.loading import load_document

from database.db_utils import doc_in_table


from tqdm import tqdm


class Controller:
    def __init__(self, db_path: Path):
        self.logger = ElicitLogger(db_path)

    def register_schema(self, schema: Path, schema_name: str) -> None:
        if len(self.functions) > 0:
            raise ValueError(
                "Must register schemas before registering labelling functions.")
        self.schemas[schema_name] = schema

    def register_labelling_function(self, labelling_function: Type[LabellingFunctionBase], function_kwargs: dict = {}) -> None:
        assert issubclass(
            labelling_function, LabellingFunctionBase), "Labelling function must be a subclass of LabellingFunctionBase."
        if self.schemas == {}:
            raise ValueError(
                "Must register schemas before registering labelling functions.")
        obj = labelling_function(schemas=self.schemas,
                                 logger=self.logger, **function_kwargs)
        self.functions.append(obj)

    def setup_db(self) -> None:
        pass

    def run(self, documents: List[Path]) -> None:
        pbar = tqdm(documents)
        for doc in pbar:
            text = load_document(doc)
            cases = []
            for function in self.functions:
                pbar.set_description(
                    f"Running {function.func.labelling_method}")
                if function.func.required_schemas:
                    schema_kwargs = {rs: self.schemas[rs]
                                     for rs in function.func.required_schemas}
                else:
                    schema_kwargs = {}
                case = function(doc=text, pdf=doc, **schema_kwargs)
                cases.append(case)
            vectorizer.combine_and_store(cases)

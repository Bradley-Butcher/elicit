"""
Main pipeline launch-point. 
Currently uses prefect to chain functions together, this will be changed in a future release.

"""
import functools
from typing import Callable, List, Optional, Set

from pathlib import Path
from elicit.document import Document


from elicit.vectorizer import Vectorizer
from elicit.utils.loading import load_document

from tqdm import tqdm

def labelling_function(
    func=None,
    labelling_method: str = None,
    required_schemas: Set[str] = None
    ):
    """
    Decorator for labelling functions.

    :param func: The function to decorate.
    :param labelling_method: The labelling method.
    :param required_schemas: The required schemas.
    """
    if not func:
        return functools.partial(labelling_function, labelling_method=labelling_method, required_schemas=required_schemas)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        assert len(args) == 0, "All arguments should be passed as keyword arguments."
        doc = Document(filename=kwargs.pop("pdf").stem, method=labelling_method)
        doc = func(document=doc, **kwargs)
        return doc
    if required_schemas:
        wrapper.required_schemas = required_schemas
    wrapper.labelling_method = labelling_method
    return wrapper

class Pipeline:
    def __init__(self, flow_weighting: Optional[dict] = None):
        self.functions = []
        self.schemas = {}
        self.flow_weighting = flow_weighting

    def register_schema(self, schema: Path, schema_name: str) -> None:
        self.schemas[schema_name] = schema

    def register_function(self, function: Callable, function_kwargs: dict = {}) -> None:
        self.functions.append(functools.partial(function, **function_kwargs))
    
    def run(self, documents: List[Path]) -> None:
        vectorizer = Vectorizer(flow_weighting=self.flow_weighting)
        pbar = tqdm(documents)
        for doc in pbar:
            text = load_document(doc)
            cases = []
            for function in self.functions:
                pbar.set_description(f"Running {function.func.labelling_method}")
                if function.func.required_schemas:
                    schema_kwargs = {rs: self.schemas[rs] for rs in function.func.required_schemas}
                else:
                    schema_kwargs = {}
                case = function(doc=text, pdf=doc, **schema_kwargs)
                cases.append(case)
            vectorizer.combine_and_store(cases)
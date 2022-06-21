"""Abstract base class for labelling functions."""
from abc import ABC, abstractmethod


class LabellingFunctionBase(ABC):

    def __init__(self, schemas: dict):
        for k, v in schemas.items():
            setattr(self, k, v)

    @abstractmethod
    @property
    def labelling_method(self):
        pass

    @abstractmethod
    def train(self, doc: str, extraction: str):
        """Train the labelling function."""
        pass

    @abstractmethod
    def extract(self, doc: str) -> str:
        """Use the labelling function to extract a label from a document."""
        pass


class CategoricalLabellingFunction(LabellingFunctionBase):

    def __init__(self, schemas: dict):
        super().__init__(schemas)

    @abstractmethod
    def train(self, doc: str, extraction: str, value: str):
        """Train the labelling function."""
        pass

    @abstractmethod
    def extract(self, doc: str) -> str:
        """Use the labelling function to extract a label from a document."""
        pass

    @abstractmethod
    @property
    def labelling_method(self):
        pass


class NumericalLabellingFunction(LabellingFunctionBase):

    def __init__(self, schemas: dict):
        super().__init__(schemas)

    @abstractmethod
    def train(self, doc: str, extraction: str, value: float):
        """Train the labelling function."""
        pass

    @abstractmethod
    def extract(self, doc: str) -> float:
        """Use the labelling function to extract a label from a document."""
        pass

    @abstractmethod
    @property
    def labelling_method(self):
        pass

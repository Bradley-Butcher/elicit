"""Script which contains the following interfaces:
 - ElicitLogger, which pushes extractions to the specified database
 - Labelling Function Abstract Classes
 - Extraction class, a dataclass which stores abstractions.
    also has various classmethods for easily extracting evidence.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from spacy.language import Language


from elicit.utils.loading import load_schema
from database.db_utils import connect_db, get_next_id, get_doc_id, get_variable_id, get_extraction_id
from elicit.utils import context_from_doc_char


class ElicitLogger:
    """
    Class which pushes an extraction, evidence, and label to the database.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db = connect_db(db_path)
        print(f"Connected to Extraction Database: {db_path}")

    def _get_doc(self, document_name: str) -> int:
        doc_id = get_doc_id(self.db, document_name)
        if doc_id >= 0:
            return doc_id
        else:
            doc_id = get_next_id(self.db, 'document')
            self.db.execute(
                "INSERT INTO document (document_id, document_name) VALUES (?, ?)", (doc_id, document_name))
            return doc_id

    def _get_variable(self, document_id: int, variable_name: str, variable_value: str) -> int:
        variable_id = get_variable_id(
            self.db, variable_name, variable_value, document_id)
        if variable_id >= 0:
            return variable_id
        else:
            var_id = get_next_id(self.db, 'variable')
            self.db.execute(
                "INSERT INTO variable (variable_id, variable_name, variable_value, document_id) VALUES (?, ?, ?, ?)", (var_id, variable_name, variable_value, document_id))
            return var_id

    def _get_extraction(self, document_id: int, variable_id: int, method: str) -> int:
        """
        Get the ID of the extraction with the given method and variable.
        :param document_id: The ID of the document.
        :param variable_id: The ID of the variable.
        :param method: The method of the extraction.
        :return: The ID of the extraction.
        """
        extraction_id = get_extraction_id(
            self.db, method, variable_id, document_id)
        if extraction_id >= 0:
            return extraction_id
        else:
            return get_next_id(self.db, 'extraction')

    def _push_evidence(self, document_id: int, variable_id: int, extraction: "Extraction", method: str):
        """
        Push the given evidence to the database.
        :param document_id: The ID of the document.
        :param variable_id: The ID of the variable.
        :param evidence: The evidence to push.
        """
        next_extraction_id = self._get_extraction(
            document_id, variable_id, method)
        self.db.execute(
            "INSERT INTO extraction (extraction_id, method, exact_context, local_context, wider_context, confidence, variable_id, document_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (next_extraction_id, method, extraction.exact_context, extraction.local_context, extraction.wider_context, extraction.confidence, variable_id, document_id))

    def push_variable(self, document_name: str, variable_name: str, variable_value: str) -> None:
        """
        Push the given value to the database.
        :param document_name: The name of the document.
        :param variable_name: The name of the variable.
        :param variable_value: The value to push.
        """
        doc_id = self._get_doc(document_name)
        var_id = self._get_variable(doc_id, variable_name, variable_value)
        self.db.commit()

    def push(self, document_name: str, variable_name: str, extraction: "Extraction", method: str):
        """
        Push the given value to the database.
        :param document_name: The name of the document.
        :param variable_name: The name of the variable.
        :param value: The value to push.
        :param evidence: The evidence to push.
        """
        assert isinstance(
            extraction, Extraction), "'extraction' must be an Extraction object."
        doc_id = self._get_doc(document_name)
        var_id = self._get_variable(doc_id, variable_name, extraction.value)
        self._push_evidence(doc_id, var_id, extraction, method)
        self.db.commit()


class LabellingFunctionBase(ABC):

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger):
        """Initialize the labelling function."""
        self.schemas = {k: v for k, v in schemas.items()}
        self.logger = logger

    @abstractmethod
    def load(self) -> None:
        """
        Load whatever is required for the labelling function,
        e.g. wordlist, model, etc.
        """
        pass

    def get_schema(self, schema_name: str, variable: str = None) -> dict:
        """Get the schema for the given schema name."""
        try:
            schema = self.schemas[schema_name]
        except KeyError:
            raise KeyError("Schema {} not found.".format(schema_name))
        if variable is not None:
            try:
                schema = schema[variable]
            except KeyError:
                raise KeyError("Variable {} not found in schema {}.".format(
                    variable, schema_name))
        return schema

    def _validate_category(self, variable_name: str, value: Union[str, float]) -> bool:
        """
        Validate the given value as a category (or float / raw value).

        :param variable_name: The name of the variable.
        :param value: The value to validate.

        :return: True if the value is a valid category, False otherwise.
        """
        if variable_name not in self.get_schema('categories'):
            return False
        if isinstance(value, float) or self.get_schema('categories', variable_name) == 'raw':
            return True
        return value in [*self.get_schema('categories', variable_name), "ABSTAIN"]

    def push(self, document_name: str, variable_name: str, extraction: "Extraction"):
        """Push the given value to the database."""
        if not self._validate_category(variable_name, extraction.value):
            raise ValueError("Value {} is not a valid category for variable {}.".format(
                extraction.value, variable_name))
        self.logger.push(document_name, variable_name,
                         extraction, self.labelling_method)

    def push_many(self, document_name: str, variable_name: str, extraction_list: List["Extraction"]) -> None:
        """
        Push the given extractions to the database.
        :param document_name: The name of the document.
        :param variable_name: The name of the variable.
        :param extractions: The extractions to push.

        :return: None
        """
        for extraction in extraction_list:
            self.push(document_name, variable_name, extraction)

    @property
    @abstractmethod
    def labelling_method(self):
        """Return the labelling method string."""
        pass

    @property
    def type(self):
        return "categorical"

    @abstractmethod
    def train(self, document_name: str, variable_name: str, extraction: "Extraction"):
        """Train the labelling function."""
        pass

    @abstractmethod
    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        """Use the labelling function to extract a label from a document."""
        pass


class CategoricalLabellingFunction(LabellingFunctionBase):

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger):
        super().__init__(schemas, logger)

    @abstractmethod
    def train(self, document_name: str, variable_name: str, extraction: "Extraction"):
        """Train the labelling function."""
        pass

    @abstractmethod
    def load(self) -> None:
        """
        Load whatever is required for the labelling function,
        e.g. wordlist, model, etc.
        """
        pass

    @abstractmethod
    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        """Use the labelling function to extract a label from a document."""
        pass

    @property
    @abstractmethod
    def labelling_method(self):
        pass

    @property
    def type(self):
        return "categorical"


class NumericalLabellingFunction(LabellingFunctionBase):

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger):
        super().__init__(schemas, logger)

    @abstractmethod
    def train(self, document_name: str, variable_name: str, extraction: "Extraction"):
        """Train the labelling function."""
        pass

    @abstractmethod
    def load(self) -> None:
        """
        Load whatever is required for the labelling function,
        e.g. wordlist, model, etc.
        """
        pass

    @abstractmethod
    def extract(self, document_name: str, variable_name: str, document_text: str) -> float:
        """Use the labelling function to extract a label from a document."""
        pass

    @property
    def type(self):
        return "numerical"

    @property
    @abstractmethod
    def labelling_method(self):
        pass


class RawLabellingFunction(LabellingFunctionBase):

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger):
        super().__init__(schemas, logger)

    @abstractmethod
    def train(self, document_name: str, variable_name: str, extraction: "Extraction"):
        """Train the labelling function."""
        pass

    @abstractmethod
    def extract(self, document_name: str, variable_name: str, document_text: str) -> str:
        """Use the labelling function to extract a label from a document."""
        pass

    @property
    def type():
        return "raw"

    @property
    @abstractmethod
    def labelling_method(self):
        pass


@dataclass
class Extraction:
    """
    Class for storing evidence.
    """
    value: str
    exact_context: str
    local_context: str
    wider_context: str
    confidence: float

    @staticmethod
    def sanitize(string: str) -> str:
        """
        Sanitize the string.
        """
        return string.strip().replace("\n", " ").replace("\t", " ").replace("'", "").replace("\"", "").replace('"', "")

    @classmethod
    def abstain(cls, confidence: float = 0) -> "Extraction":
        """Abstains, providing no evidence"""
        return cls("ABSTAIN", None, None, None, confidence)

    @classmethod
    def from_character_startend(cls, doc: str, value: str, confidence: float, start: int, end: int, local_padding: int = 100, wider_padding: int = 500, max_chars: int = 100) -> "Extraction":
        """
        Returns an evidence object from a character start and end index.

        :param doc: The document.
        :param confidence: The confidence of the extraction.
        :param start: The start index.
        :param end: The end index.
        :param local_padding: The padding for the local context.
        :param wider_padding: The padding for the wider context.
        :param max_chars: The maximum number of characters to extract.

        :return: An Extraction object.
        """
        mid = (start + end) // 2
        start = int(max(start, mid - (max_chars / 2)))
        end = int(min(end, mid + (max_chars / 2)))
        exact_context = context_from_doc_char(doc, start, end, padding=0)
        local_context = context_from_doc_char(doc, start, end, local_padding)
        wider_context = context_from_doc_char(doc, start, end, wider_padding)
        exact_context = cls.sanitize(exact_context)
        local_context = cls.sanitize(local_context)
        wider_context = cls.sanitize(wider_context)
        return cls(value, exact_context, local_context, wider_context, confidence)

    @classmethod
    def from_string(cls, string: str, value: str, confidence: float, exact_chars: int = 100, local_padding: int = 100, wider_padding: int = 500) -> "Extraction":
        """
        Returns an evidence object from a string.

        :param string: The string to extract from.
        :param confidence: The confidence of the extraction.
        :param exact_chars: The number of characters to use for the exact context.
        :param local_padding: The number of characters to use for the local context.
        :param wider_padding: The number of characters to use for the wider context.

        :return: An Extraction object.
        """
        mid = len(string) // 2
        exact_context = string[max(
            0, mid - (exact_chars // 2)):min(len(string), mid + (exact_chars // 2))]
        local_context = string[max(0, mid - (exact_chars + local_padding // 2)):min(
            len(string), mid + (exact_chars + local_padding // 2))]
        wider_context = string[max(0, mid - (exact_chars + wider_padding // 2)):min(
            len(string), mid + (exact_chars + wider_padding // 2))]
        exact_context = cls.sanitize(exact_context)
        local_context = cls.sanitize(local_context)
        wider_context = cls.sanitize(wider_context)
        return cls(value, exact_context, local_context, wider_context, confidence)

    @classmethod
    def from_spacy(cls, doc: Language, value: str, confidence: float, start: int, end: int, local_padding: int = 0, wider_padding: int = 10) -> "Extraction":
        """
        Returns an evidence object from a character start and end index.

        :param doc: The document.
        :param start: The start index.
        :param end: The end index.
        :param local_padding: The padding for the local context.
        :param wider_padding: The padding for the wider context.

        :return: An Extraction object.
        """
        exact_context = doc[start:end]
        local_start = max(0, start - local_padding)
        local_end = min(len(doc), end + local_padding)
        local_context = doc[local_start:local_end]
        wider_start = max(0, start - wider_padding)
        wider_end = min(len(doc), end + wider_padding)
        wider_context = doc[wider_start:wider_end]
        exact_context = cls.sanitize(exact_context.text)
        local_context = cls.sanitize(local_context.text)
        wider_context = cls.sanitize(wider_context.text)
        return cls(value, exact_context, local_context, wider_context, confidence)

    @classmethod
    def from_spacy_multiple(cls, doc: Language, value: str, confidence: float, evidence_list: List[Tuple[str, int, int]], wider_padding: int = 20) -> "Extraction":
        """
        Returns an evidence object from a character start and end index.

        :param doc: The document.
        :param evidence_list: A list of evidence.
        :param wider_padding: The padding for the wider context.

        :return: An Extraction object.
        """
        local_context = ", ".join([span for span, _, _ in evidence_list])
        widers = []
        for span, start, end in evidence_list:
            start = max(0, start - wider_padding)
            end = min(len(doc), end + wider_padding)
            widers.append(doc[start:end].text)
        wider_context = " | ".join(widers)
        local_context = cls.sanitize(local_context)
        wider_context = cls.sanitize(wider_context)
        return cls(value, local_context, local_context, wider_context, confidence)

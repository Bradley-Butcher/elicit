"""Script which contains the following interfaces:
 - ElicitLogger, which pushes extractions to the specified database
 - Labelling Function Abstract Classes
 - Extraction class, a dataclass which stores abstractions.
    also has various classmethods for easily extracting evidence.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from sqlite3 import IntegrityError
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
from numpy import var

from spacy.language import Language


from elicit.utils.loading import load_schema
from database.db_utils import connect_db, get_next_id, get_doc_id, get_variable_id, get_extraction_id, query_db
from elicit.utils import context_from_doc_char


class ElicitLogger:
    """
    Class which pushes an extraction, evidence, and label to the database.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db = connect_db(db_path)
        print(f"Connected to Extraction Database: {db_path}")

    def doc_in(self, document_name: str) -> bool:
        return get_doc_id(self.db, document_name) >= 0

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

    def find_matching_evidence(self, document_id: int, variable_id: int, extraction: "Extraction"):
        """
        Check the database to see if any extractions have previously identified the same evidence.
        :param document_id: The ID of the document.
        :param variable_id: The ID of the variable.
        :param evidence: The evidence to match.
        :return: The ID of the matching evidence, or -1 if no matching evidence is found.
        """
        if extraction.exact_context is None:
            return -1
        for row in self.db.execute("SELECT extraction_id, exact_context, local_context, wider_context FROM extraction WHERE variable_id = ? AND document_id = ?", (variable_id, document_id)):
            if row[1] is None:
                continue
            if row[1] in extraction.local_context or extraction.exact_context in row[2]:
                return row[0]
        return -1

    def _check_duplicate(self, extraction_id: int, method: str, extraction: "Extraction"):
        row = query_db(
            self.db, "SELECT confidence FROM raw_extraction WHERE extraction_id = ? AND method = ?", (extraction_id, method))
        if len(row) > 0:
            if float(row[0][0]) < extraction.confidence:
                self.db.execute("UPDATE raw_extraction SET confidence = ? WHERE extraction_id = ? AND method = ?", (
                    extraction.confidence, extraction_id, method))
            return True
        return False

    def _push_evidence(self, document_id: int, variable_id: int, extraction: "Extraction", method: str):
        """
        Push the given evidence to the database.
        :param document_id: The ID of the document.
        :param variable_id: The ID of the variable.
        :param evidence: The evidence to push.
        """
        extraction_id = self.find_matching_evidence(
            document_id, variable_id, extraction)
        if extraction_id < 0:
            extraction_id = get_next_id(self.db, 'extraction')
            self.db.execute(
                "INSERT INTO extraction (extraction_id, exact_context, local_context, wider_context, variable_id, document_id) VALUES (?, ?, ?, ?, ?, ?)", (extraction_id, extraction.exact_context, extraction.local_context, extraction.wider_context, variable_id, document_id))
        if not self._check_duplicate(extraction_id, method, extraction):
            raw_extraction_id = get_next_id(self.db, 'raw_extraction')
            self.db.execute("INSERT INTO raw_extraction (raw_extraction_id, extraction_id, method, confidence) VALUES (?, ?, ?, ?)",
                            (raw_extraction_id, extraction_id, method, extraction.confidence))

    def push_variable(self, document_name: str, variable_name: str, variable_value: str) -> None:
        """
        Push the given value to the database.
        :param document_name: The name of the document.
        :param variable_name: The name of the variable.
        :param variable_value: The value to push.
        """
        doc_id = self._get_doc(document_name)
        var_id = self._get_variable(doc_id, variable_name, variable_value)
        self._push_evidence(doc_id, var_id, Extraction.not_present(
            variable_value), "manual")
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

    def get_validated_document_names(self, variable: str, include_negative: bool) -> List[str]:
        """
        Get the list of documents which have the given variable.
        :param variable: The variable to check.
        :return: The list of documents.
        """
        cond = "= 'TRUE'" if not include_negative else "IS NOT NULL"
        results = self.db.execute(
            f"""
                SELECT document.document_name FROM extraction 
                LEFT JOIN variable
                ON extraction.variable_id = variable.variable_id 
                LEFT JOIN document 
                ON document.document_id = variable.document_id  
                WHERE extraction.valid {cond} AND variable.variable_name = ?
            """, (variable,)).fetchall()
        return [result[0] for result in results]

    def get_validated_extractions(self, document_names: List[str], variable: str, include_negative: bool):
        """
        Get the list of validated extractions for the given document and variable.

        :param document_names: The list of documents to check.
        :param variable: The variable to check.

        :return: The list of extractions.
        """
        cond = "= 'TRUE'" if not include_negative else "IS NOT NULL"
        cursor = self.db.execute(
            f"""
                SELECT DISTINCT document.document_name, variable.variable_value, extraction.exact_context, extraction.local_context, extraction.wider_context, extraction.confidence, extraction.valid, extraction.validated_context FROM extraction 
                LEFT JOIN variable
                ON extraction.variable_id = variable.variable_id 
                LEFT JOIN document 
                ON document.document_id = variable.document_id  
                WHERE extraction.valid {cond} AND variable.variable_name = '{variable}'
            """)
        return [Extraction(row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in cursor if row[0] in document_names]


class LabellingFunctionBase(ABC):

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger, top_k: int = -1):
        """Initialize the labelling function."""
        self.schemas = {k: v for k, v in schemas.items()}
        self.logger = logger
        self.loaded = False
        self.top_k = top_k

    @abstractmethod
    def load(self, model_directory: Path, device: Union[int, str]) -> None:
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
        sorted_extractions = sorted(
            extraction_list, key=lambda x: x.confidence, reverse=True)
        if self.top_k > 0:
            sorted_extractions = sorted_extractions[:self.top_k]
        for extraction in sorted_extractions:
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
    def train(self, data: dict[str, List["Extraction"]]):
        """Train the labelling function."""
        pass

    @abstractmethod
    def extract(self, document_name: str, variable_name: str, document_text: str) -> None:
        """Use the labelling function to extract a label from a document."""
        pass


class CategoricalLabellingFunction(LabellingFunctionBase):

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger, top_k: int = -1):
        super().__init__(schemas, logger, top_k)

    @abstractmethod
    def train(self, data: dict[str, List["Extraction"]]):
        """Train the labelling function."""
        pass

    @abstractmethod
    def load(self, model_directory: Path, device: Union[int, str]) -> None:
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

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger, top_k=-1):
        super().__init__(schemas, logger, top_k)

    @abstractmethod
    def train(self, data: dict[str, List["Extraction"]]):
        """Train the labelling function."""
        pass

    @abstractmethod
    def load(self, model_directory: Path, device: Union[int, str]) -> None:
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

    def __init__(self, schemas: dict[str, Path], logger: ElicitLogger, top_k=-1):
        super().__init__(schemas, logger, top_k)

    @abstractmethod
    def load(self, model_directory: Path, device: Union[int, str]) -> None:
        """
        Load whatever is required for the labelling function,
        e.g. wordlist, model, etc.
        """
        pass

    @abstractmethod
    def train(self, data: dict[str, List["Extraction"]]):
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
    valid: bool
    validated_context: str

    @staticmethod
    def sanitize(string: str) -> str:
        """
        Sanitize the string.
        """
        return string.strip().replace("\n", " ").replace("\t", " ").replace("'", "").replace("\"", "").replace('"', "")

    @classmethod
    def abstain(cls, confidence: float = 0) -> "Extraction":
        """Abstains, providing no evidence"""
        return cls("ABSTAIN", None, None, None, confidence, None, None)

    @classmethod
    def not_present(cls, value: str):
        """Not present, providing no evidence"""
        return cls(value, None, None, None, 0, None, None)

    @classmethod
    def from_character_startend(cls, doc: str, value: str, confidence: float, start: int, end: int, local_padding: int = 75, wider_padding: int = 300, max_chars: int = 100) -> "Extraction":
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
        exact_context = context_from_doc_char(doc, start, end, padding=0)
        mid = (start + end) // 2
        start = int(max(start, mid - (max_chars / 2)))
        end = int(min(end, mid + (max_chars / 2)))
        local_context = context_from_doc_char(doc, start, end, local_padding)
        wider_context = context_from_doc_char(doc, start, end, wider_padding)
        exact_context = cls.sanitize(exact_context)
        local_context = cls.sanitize(local_context)
        wider_context = cls.sanitize(wider_context)
        return cls(value, exact_context, local_context, wider_context, confidence, None, None)

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
        return cls(value, exact_context, local_context, wider_context, confidence, None, None)

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
        return cls(value, exact_context, local_context, wider_context, confidence, None, None)

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
        return cls(value, local_context, local_context, wider_context, confidence, None, None)

"""Script which merges multiple cases and stores them in a database."""
from typing import Dict, List, Set, Tuple
from elicit.case import Case, CaseField, Evidence
from dataclasses import asdict, dataclass
from database.db_utils import connect_db, insert_doc_from_dict

@dataclass
class Output:
    """
    Class which represents the output, and output vectors, of the vectorizer.
    """
    methods: List[str]
    vector: List[float]
    evidence: List[Evidence]

    def get_vector(self, method: str) -> List[float]:
        """
        Returns the vector of the given method.
        :param method: The method to get the vector for.
        """
        return self.vector[self.methods.index(method)]
    
    def get_evidence(self, method: str) -> List[Evidence]:
        """
        Returns the evidence of the given method.
        :param method: The method to get the evidence for.
        """
        return self.evidence[self.methods.index(method)]

class Vectorizer:
    """
    Class which takes the output cases from 
    multiple flows and combines them into a vector format 
    that matches the database schema.
    
    :param flow_weighting: A dictionary of flow names and their weighting.
    """
    def __init__(self, flow_weighting: dict[str, float] = None) -> None:
        self.flow_weighting = flow_weighting
        self.db = connect_db()
        print("Connected to results database.")
    
    @staticmethod
    def match_cases(cases: List[Case]) -> Dict[str, List[Case]]:
        """
        Matches cases from different flows.

        :param cases: The cases to match.
        """
        matches = {}
        for c in cases:
            if c.filename not in matches:
                matches[c.filename] = [c]
            else:
                matches[c.filename].append(c)
        return matches
    
    def apply_weighting(self, cases: List[Case]) -> List[Case]:
        """
        Apply the weighting to the case confidence.

        :param cases: The cases to apply the weighting to.
        """
        new_cases = []
        for case in cases:
            assert case.method in self.flow_weighting, f"Unrecognized method: {case.method} in weighting dict with keys: {self.flow_weighting.keys()}"
            weight = self.flow_weighting[case.method]
            new_case = Case(case.filename, case.method)
            weighted_dict = {k: v * weight for k, v in case.to_dict().items()}
            new_case.add_dict(weighted_dict)
            new_cases.append(new_case)
        return new_cases
    
    def identify_methods(self, cases: List[Case]) -> List[str]:
        """
        Identifies the methods used in the cases.

        :param cases: The cases to identify the methods for.
        """
        self.methods = list({case.method for case in cases})

    def combine_and_store(self, cases: List[Case]) -> Dict[str, Case]:
        """
        Combines cases from multiple flows and stores them in the database.
        
        :param cases: The cases to combine.
        """
        matched_cases = Vectorizer.match_cases(cases)
        self.identify_methods(cases)
        if self.flow_weighting:
            matched_cases = self.apply_weighting(matched_cases)
        for name, mcases in matched_cases.items():
            case = self.vectorize(mcases)
            insert_doc_from_dict(self.db, name, case)
        self.db.commit()

    @staticmethod
    def get_key_list(cases: List[Case]) -> Set[str]:
        """
        Returns a list of keys for the given cases.
        
        :param cases: The cases to get the keys for.
        """
        keys = []
        for c in cases:
            keys = keys + [str(k) for k in c.to_dict().keys()]
        return set(keys)

    def get_output_value(self, case_group: List[str], key: str, value: str) -> Tuple[List[float], Evidence, List[str]]:
        """
        Returns a list of methods, evidence, and vectors for a list of cases.
        These cases are actually single case, but produced by multiple flows. 
        This is the function where they are combined before storage.

        :param case_group: The cases to get the methods and vectors for.
        :param key: The key to get the methods and vectors for.
        :param value: The value to get the methods and vectors for.
        """
        local_methods = [case.method for case in case_group if key in case.to_dict()]
        methods = [m for m in self.methods if m in local_methods]
        vectors = [0 for _ in range(len(methods))]
        evidence = ["" for _ in range(len(methods))]
        for case in case_group:
            if not key in case.to_dict():
                continue
            idx = methods.index(case.method)
            if not hasattr(case, key):
                continue
            variable_value = getattr(case, key)
            if isinstance(variable_value, CaseField):
                if variable_value.value == value:
                    vectors[idx] = variable_value.confidence
                    evidence[idx] = variable_value.evidence
                else:
                    vectors[idx] = 0
                    evidence[idx] = Evidence.no_match()
            elif isinstance(variable_value, list):        
                for f in variable_value:
                    if f.value == value:
                        vectors[idx] = f.confidence
                        evidence[idx] = f.evidence
                        break
                if not evidence[idx]:
                    vectors[idx] = 0
                    evidence[idx] = Evidence.no_match()
        return vectors, evidence, methods

    @staticmethod
    def get_value_list(cases: List[Case], key: str) -> List[str]:
        """
        Returns a list of values for the case, for a particular field.
        E.g. the list of values for the "victim_age" field, [42, 41, 22].
        This will be applied to one "case" but multiple case objects coming from different flows.

        :param cases: The case objects to get the values for.
        """
        values = []
        for case in cases:
            if not hasattr(case, key):
                continue
            variable_value = getattr(case, key)
            if isinstance(variable_value, CaseField):
                values.append(variable_value.value)
            else:
                for cf in variable_value:
                    values.append(cf.value)
        return sorted(values)

    def vectorize(self, case_group: List[Case]) -> Dict[str, Dict[str, Output]]:
        """
        Vectorizes the cases. Generates a dictionary which can be inserted into the database.

        :param case_group: The list of cases to vectorize. These are single cases, but produced by multiple flows.
        """
        outputs = {}
        for key in Vectorizer.get_key_list(case_group):
            output_values = {}
            for value in Vectorizer.get_value_list(case_group, key):
                vector, evidence, methods = self.get_output_value(case_group, key, value)
                output_values[value] = asdict(Output(methods, vector, evidence))
            outputs[key] = output_values
        return outputs

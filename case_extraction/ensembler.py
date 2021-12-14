from collections import Counter
from typing import Dict, List, Literal, Optional, Set, Tuple
from case_extraction.case import Case, CaseField, Evidence
from dataclasses import asdict, dataclass

@dataclass
class Output:
    """
    Class which represents the output, and output vectors, of the ensembler.
    """
    methods: List[str]
    vector: List[float]
    evidence: List[Evidence]

    def get_vector(self, method: str) -> List[float]:
        """
        Returns the vector of the given method.
        """
        return self.vector[self.methods.index(method)]
    
    def get_evidence(self, method: str) -> List[Evidence]:
        """
        Returns the evidence of the given method.
        """
        return self.evidence[self.methods.index(method)]



class Ensembler:
    """Class which takes the output cases from multiple flows and combines them."""
    def __init__(self, mode: Literal["majority", "top", "vector"], k: Optional[int] = None, flow_weighting: dict[str, float] = None, majority_threshold: Optional[float] = None) -> None:
        self.mode = mode
        self.k = k
        self.flow_weighting = flow_weighting
        self.majority_threshold = majority_threshold
    
    @staticmethod
    def match_cases(cases: List[Case]) -> Dict[str, List[Case]]:
        """Matches cases from different flows."""
        matches = {}
        for c in cases:
            if c.filename not in matches:
                matches[c.filename] = [c]
            else:
                matches[c.filename].append(c)
        return matches
    
    def apply_weighting(self, cases: List[Case]) -> List[Case]:
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
        """Returns a list of methods."""
        self.methods = list({case.method for case in cases})

            
    def combine(self, cases: List[Case]) -> Dict[str, Case]:
        """Combines cases from multiple flows."""
        matched_cases = Ensembler.match_cases(cases)
        self.identify_methods(cases)
        if self.flow_weighting:
            matched_cases = self.apply_weighting(matched_cases)
        combined_cases = {}
        for name, mcases in matched_cases.items():
            if self.mode == "majority":
                case = self.combine_majority(mcases, self.majority_threshold)
            elif self.mode == "top":
                case = self.combine_top(mcases)
            elif self.mode == "vector":
                case = self.vectorize(mcases)
            else:
                raise ValueError("Unknown mode: {}".format(self.mode))
            combined_cases[name] = case
        return combined_cases

    @staticmethod
    def get_key_list(cases: List[Case]) -> Set[str]:
        """Returns a list of keys for the given cases."""
        keys = []
        for c in cases:
            keys = keys + [str(k) for k in c.to_dict().keys()]
        return set(keys)
    

    @staticmethod
    def group_by_case(cases: List[Case]) -> Dict[str, List[Case]]:
        """Groups cases by filename."""
        groups = {}
        for c in cases:
            if c.filename not in groups:
                groups[c.filename] = [c]
            else:
                groups[c.filename].append(c)
        return groups

    @staticmethod
    def combine_field(case_group: List[Case], field_name: str) -> List[CaseField]:
        N = 0
        field_counts = Counter()
        for case in case_group:
            case_dict = case.to_dict()
            if field_name not in case_dict:
                continue
            N += 1
            if isinstance(case_dict[field_name], CaseField):
                    field_counts[case_dict[field_name].value] += 1
            else:
                for f in case_dict[field_name]:
                        field_counts[f.value] += 1
        return [CaseField(k, v / N, "") for k, v in field_counts.items() if v / N >= 0.5]

    
    def combine_majority(self, cases: List[Case], threshold: float) -> Case:
        case_obj = Case(cases[0].filename, "ensemble")
        field_keys = self.get_key_list(cases)
        for key in field_keys:
            setattr(case_obj, key, Ensembler.combine_field(cases, key))
        return case_obj

    def get_output_value(self, case_group: List[str], key: str, value: str) -> Tuple[List[str], List[float]]:
        """
        Returns a list of methods and vectors for the given cases.
        """
        local_methods = [case.method for case in case_group]
        methods = [m for m in self.methods if m in local_methods]
        vectors = [0 for _ in range(len(methods))]
        evidence = ["" for _ in range(len(methods))]
        for case in case_group:
            idx = methods.index(case.method)
            if not hasattr(case, key):
                continue
            variable_value = getattr(case, key)
            if isinstance(variable_value, CaseField):
                if variable_value.value == value:
                    vectors[idx] = variable_value.confidence
                    evidence[idx] = variable_value.evidence
            elif isinstance(variable_value, list):
                for f in variable_value:
                    if f.value == value:
                        vectors[idx] = f.confidence
                        evidence[idx] = f.evidence
        return vectors, evidence, methods

    @staticmethod
    def get_value_list(cases: List[Case], key: str) -> List[str]:
        """Returns a list of values for the given cases."""
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
        return values

    def vectorize(self, case_group: List[Case]) -> Dict[str, Dict[str, Output]]:
        """
        Vectorizes the cases.
        """
        outputs = {}
        for key in Ensembler.get_key_list(case_group):
            output_values = {}
            for value in Ensembler.get_value_list(case_group, key):
                vector, evidence, methods = self.get_output_value(case_group, key, value)
                output_values[value] = asdict(Output(str(case_group[0].filename), methods, vector, evidence))
            outputs[key] = output_values
        return outputs

    def combine_top(self, cases: List[Case]) -> Case:
        pass

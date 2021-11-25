from collections import Counter
from typing import Dict, List, Literal, Optional, Set
from case_extraction.case import Case, CaseField

class ExtracteeSet:

    def __init__(self, name: str, extractees: List[CaseField]) -> None:
        self.name = name
        self.extractees = []
    
    def __str__(self) -> str:
        return "\n".join([str(e) for e in self.extractees])


class Ensembler:
    """Class which takes the output cases from multiple flows and combines them."""
    def __init__(self, mode: Literal["majority", "top"], k: Optional[int] = None, flow_weighting: dict[str, float] = None) -> None:
        self.mode = mode
        self.k = k
        self.flow_weighting = flow_weighting
    
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

            
    def combine(self, cases: List[Case]) -> Dict[str, Case]:
        """Combines cases from multiple flows."""
        matched_cases = Ensembler.match_cases(cases)
        if self.flow_weighting:
            matched_cases = self.apply_weighting(matched_cases)
        combined_cases = {}
        for name, mcases in matched_cases.items():
            if self.mode == "majority":
                case = self.combine_majority(mcases)
            elif self.mode == "top":
                case = self.combine_top(mcases)
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
            
    def combine_majority(self, cases: List[Case]) -> Case:
        dicts = [c.to_dict() for c in cases]
        case = Case(cases[0].filename, "ensemble")
        for key in Ensembler.get_key_list(cases):
            values = [d[key].value for d in dicts if d[key]]
            values_counter = Counter(values)
            most_common, most_common_count = values_counter.most_common(1)[0]
            mc_prop = most_common_count / len(values)
            if mc_prop >= 0.5:
                setattr(case, key, CaseField(most_common, mc_prop, ""))
            else:
                setattr(case, key, CaseField("unknown", 0, ""))
        return case


    def combine_top(self, cases: List[Case]) -> Case:
        pass

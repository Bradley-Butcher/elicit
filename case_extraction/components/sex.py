"""This script contains various components for inferring gender."""
from prefect import task
import requests
import json

from case_extraction.case import Case, CaseField

def get_gender_from_api(name: str) -> dict:
    """
    Query genderize api to get gender from name.

    :param name: name to find gender for.

    :return: dict of gender: score
    """
    request = requests.get(f"https://api.genderize.io?name={name}")
    results = json.loads(request.text)
    return results

@task
def sex_from_name(case: Case) -> Case:
    """
    Get sex from name.

    :param case: The case to update with the sex.

    :returns: the updated case object.
    """

    if isinstance(case.victims, list):
        victim_fname = [v.value.split(" ")[0] for v in case.victims]
        victim_fname = victim_fname[0]
    else:
        victim_fname = case.victims.value.split(" ")[0]

    if isinstance(case.victims, list):
        defendant_fname = [v.value.split(" ")[0] for v in case.defendants]
        defendant_fname = defendant_fname[0]
    else:
        defendant_fname = case.defendants.value.split(" ")[0]
    vsex = get_gender_from_api(victim_fname)
    dsex = get_gender_from_api(defendant_fname)
    case.victim_sex = CaseField(value=vsex["gender"], confidence=vsex["probability"], evidence=victim_fname)
    case.offender_sex = CaseField(value=dsex["gender"], confidence=dsex["probability"], evidence=defendant_fname)
    return case
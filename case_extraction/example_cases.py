from pathlib import Path
from typing import List
from case_extraction.case import Case


def load_test_cases() -> List[Case]:
    case_1 = Case(
        filename="R_-v-_Keith_Wallis.pdf",
        offenses="misconduct in public office",
        defendants="keith wallis",
        premeditated="not premeditated",
        weapon="none",
        vulnerable_victim="not vulnerable",
        prior_convictions="no prior convictions",
        physical_abuse="no physical abuse",
        emotional_abuse="no emotional abuse",
        age_mitigating="age not mitigating",
        race_aggrevating="race not an aggrevating factor",
        religious_aggrevating="religion not an aggrevating factor",
        offender_confession="no confession",
        victim_sex="",
        victim_age="",
        offender_age="",
        offender_sex="male",
        relationship="none",
        victims="mr randall",
        outcome="12 months inprisonment")

    # case_2 = Case.from_manual(
    #     filename="Sentencing_remarks_of_Mr_Justice_Openshaw:_R_-v-_Stephen_Port.pdf",
    #     defendants=["stephen port"],
    #     victims=["victim a", "victim b", "anthony walgate", "victim c", "victim d",
    #              "victim e", "victim f", "victim g", "jack taylor", "victim h", "gabriel kovari", "daniel whitworth"],
    #     charges=["murder", "rape", "administering a substance with intent"],
    #     mitigating_circumstances=["no previous convictions"],
    #     aggravating_circumstances=[],
    #     outcome=["life inprisonment", "22 years inprisonment", "10 years inprisonment"])
    case_3 = Case(
        filename="Sentencing_remarks_of_His_Honour_Judge_Eccles_Q.C._R_-v-_Ben_Blakeley.pdf",
        offenses={"murder", "obstruction of justice"},
        defendants="ben blakeley",
        victims="jayden parkinson",
        premeditated="not premeditated",
        weapon="none",
        vulnerable_victim="vulnerable",
        prior_convictions="prior convictions",
        physical_abuse="physical abuse",
        emotional_abuse="emotional abuse",
        age_mitigating="age mitigating",
        race_aggrevating="race not an aggrevating factor",
        religious_aggrevating="religion not an aggrevating factor",
        offender_confession="no confession",
        victim_sex="female",
        victim_age="17",
        offender_age="22",
        offender_sex="male",
        relationship="partner",
        outcome={"life inprisonment", "minimum 20 years"}
    )

    case_4 = Case(
        filename="R_-v-_Pavlo_Lapshyn.pdf",
        offenses={"murder", "causing an explosion with an intent to endanger life",
                  "engaging in conduct in preparation of terrorist acts"},
        premeditated="premeditated",
        weapon="knife",
        vulnerable_victim="vulnerable",
        prior_convictions="no prior convictions",
        physical_abuse="no physical abuse",
        emotional_abuse="no emotional abuse",
        age_mitigating="age mitigating",
        race_aggrevating="race an aggrevating factor",
        religious_aggrevating="religion an aggrevating factor",
        offender_confession="confession",
        victim_sex="male",
        victim_age="82",
        offender_age="25",
        offender_sex="male",
        relationship="none",
        victims={"mohammed saleem chaudhry", "mr saleem"},
        defendants={"pavlo lapshyn"},
        outcome={"40 years inprisonment", "life inprisonment"}
    )

    # case_5 = Case.from_manual(
    #     filename="R_-v-_Elliot_Bower,_Declan_Bower,_Mason_Cartledge:_Sentencing_remarks_of_HHJ_Jeremy_Richardson_QC.pdf",
    #     defendants=["elliot bower", "declan bower", "mason cartledge"],
    #     victims=["adnan ashraf", "mohammed usman bin adnan", "miroslav duna",
    #              "vlasta dunova", "nicola dunova", "livia matova", "erica kroscenova"],
    #     charges=["causing death by dangerous driving", "causing serious injury by dangerous driving",
    #              "possession of cannabis", "failing to surrender to bail", "aggrevated taking of a vehicle"],
    #     mitigating_circumstances=["age"],
    #     aggravating_circumstances=[
    #         "previous convictions"],
    #     outcome=["11 years inprisonment"])

    return [case_1, case_3, case_4]


def load_train_cases() -> List[Case]:
    case_1 = Case.from_manual(
        filename="R_-v-_Colin_Ash-Smith.pdf",
        defendants=["colin ash-smith"],
        victims=["claire tiltman"],
        charges=["murder"],
        mitigating_circumstances=[],
        aggravating_circumstances=[
            "premeditated", "planned", "other convictions", "vulnerable victim"],
        outcome=["life inprisonment, minimum 21 years"])
    return [case_1]

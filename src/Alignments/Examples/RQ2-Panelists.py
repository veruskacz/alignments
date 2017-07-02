import Alignments.Settings as St
import Alignments.UserActivities.UserRQ as Urq
from Alignments.Linksets.SPA_LinksetRefine import refine
from Alignments.Linksets.SPA_LinksetSubset import specification_2_linkset_subset
from Alignments.Linksets.SPA_Linkset import specs_2_linkset, specs_2_linkset_intermediate  # , specs_2_linkset_id

################################################################################################
""" RESEARCH QUESTIONS: 1 - What paintings did Rembrandt paint? """
"""

"""
################################################################################################

"""
    Question URI: http://risis.eu/activity/idea_479e32
    Label: Does the collocation of applicants and panel members in an organisation influence the panel decision?

    http://risis.eu/genderc/panels | http://risis.eu/genderc/vocab/Panel | 25 instances found
	http://risis.eu/dataset/Panellists | http://risis.eu/Panellists/ontology/class/Panelists | 348 instances found
	http://risis.eu/genderc/Applicant | http://xmlns.com/foaf/0.1/Person | 27119 instances found
	http://risis.eu/genderc/Applicant | http://risis.eu/genderc/vocab/AffiliationDetail | 27119 instances found
	http://risis.eu/genderc/Applicant | http://risis.eu/genderc/vocab/Applicant | 27119 instances found
	http://risis.eu/genderc/Applicant | http://risis.eu/genderc/vocab/RelationDetail | 27119 instances found
	http://risis.eu/genderc/Application | http://risis.eu/genderc/vocab/Application | 3030 instances found
	http://risis.eu/genderc/Evaluation | http://risis.eu/genderc/vocab/Evaluation | 3030 instances found


    1 - http://risis.eu/activity/idea_algmt_d0e49c
    subjectsTarget   :	http://risis.eu/dataset/Panellists
    objectsTarget    :	http://risis.eu/genderc/panels
    subjectsDatatype :	http://risis.eu/Panellists/ontology/class/Panelists
    objectsDatatype  :	http://risis.eu/genderc/vocab/Panel
    alignsSubjects   :	http://risis.eu/Panellists/ontology/predicate/Discipline
    alignsObjects    :	http://risis.eu/genderc/vocab/panelID
    >>> created      : 	http://risis.eu/linkset/Panellists_panels_exactStrSim_Discipline_N629827418 | 348 correspondences found

    2 - http://risis.eu/activity/idea_algmt_3614c7
    subjectsTarget   :	http://risis.eu/genderc/Application
    objectsTarget    :	http://risis.eu/genderc/Applicant
    subjectsDatatype :	http://risis.eu/genderc/vocab/Application
    objectsDatatype  :	http://risis.eu/genderc/vocab/Applicant
    alignsSubjects   :	http://risis.eu/genderc/vocab/applicant
    alignsObjects    :	http://risis.eu/alignment/predicate/resourceIdentifier
    >>> created      : 	http://risis.eu/linkset/subset_Application_Applicant_embededAlignment_applicant_P1844596270 | 3030 correspondences found

    3 - http://risis.eu/activity/idea_algmt_e3dfc1
    subjectsTarget   :	http://risis.eu/genderc/Application
    objectsTarget    :	http://risis.eu/genderc/panels
    subjectsDatatype :	http://risis.eu/genderc/vocab/Application
    objectsDatatype  :	http://risis.eu/genderc/vocab/Panel
    alignsSubjects   :	http://risis.eu/genderc/vocab/panel
    alignsObjects    :	http://risis.eu/alignment/predicate/resourceIdentifier
    >>> created      : 	http://risis.eu/linkset/subset_Application_panels_embededAlignment_panel_N96174508 | 3030 correspondences found

    4 - http://risis.eu/activity/idea_algmt_bf3a85
    subjectsTarget   :	http://risis.eu/genderc/Application
    objectsTarget    :	http://risis.eu/genderc/Evaluation
    subjectsDatatype :	http://risis.eu/genderc/vocab/Application
    objectsDatatype  :	http://risis.eu/genderc/vocab/Evaluation
    alignsSubjects   :	http://risis.eu/genderc/vocab/evaluation
    alignsObjects    :	http://risis.eu/alignment/predicate/resourceIdentifier
    >>> created      : 	http://risis.eu/linkset/subset_Application_Evaluation_embededAlignment_evaluation_P1993444604 | 3030 correspondences found

    5 - http://risis.eu/activity/idea_algmt_a9ac69
    subjectsTarget   :	http://risis.eu/genderc/Applicant
    objectsTarget    :	http://risis.eu/dataset/Panellists
    subjectsDatatype :	http://risis.eu/genderc/vocab/Applicant
    objectsDatatype  :	http://risis.eu/Panellists/ontology/class/Panelists
    alignsSubjects   :	http://risis.eu/genderc/vocab/affiliation
    alignsObjects    :	http://risis.eu/Panellists/ontology/predicate/Name_of_home_institution
    >>> created      : 	http://risis.eu/linkset/Applicant_Panellists_exactStrSim_affiliation_N6291229 | 212 correspondences found
"""

# TODO: check for space in the uri
ds_Panel = "http://risis.eu/genderc/panels"
ds_Panellist = "http://risis.eu/dataset/Panellists"
ds_evaluation = "http://risis.eu/genderc/Evaluation"
ds_Applicants = "http://risis.eu/genderc/Applicant"
ds_Application = "http://risis.eu/genderc/Application"

################################################################################################
""" 1: REGISTER YOUR RESEARCH QUESTION """
################################################################################################
question = "2 - Does the collocation of applicants and panel members in an organisation influence the panel decision?"
research_qst = Urq.register_research_question(question)
research_uri = research_qst[St.result]

################################################################################################
""" 2: REGISTER A DATASET MAPPING: A PAIR OF [DATASET|ENTITY TYPE] """
################################################################################################
ds_mapping = {
    ds_Panel: ["http://risis.eu/genderc/vocab/Panel"],
    ds_Panellist: ["http://risis.eu/Panellists/ontology/class/Panelists"],
    ds_Applicants: ["http://xmlns.com/foaf/0.1/Person", "http://risis.eu/genderc/vocab/AffiliationDetail",
                    "http://risis.eu/genderc/vocab/Applicant", "http://risis.eu/genderc/vocab/RelationDetail"],
    ds_Application: ["http://risis.eu/genderc/vocab/Application"],
    ds_evaluation: ["http://risis.eu/genderc/vocab/Evaluation"]}
Urq.register_dataset_mapping(question_uri=research_uri, mapping=ds_mapping, activated=False)



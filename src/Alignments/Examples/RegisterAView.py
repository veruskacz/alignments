import Alignments.Settings as St
import Alignments.NameSpace as Ns
from Alignments.Query import display_result
from Alignments.UserActivities.View import view

# THIS ASSUMES THAT THE RESEARCH QUESTION, THE VIEW_LENS, T
# HE DATASETS AND THERE PROPERTIES ALL EXIST IN THE TRIPLE STORE


###############################################################################################################
###############################################################################################################
""" DEFINE VIEW SPECIFICATION RESULTS """
###############################################################################################################
###############################################################################################################

# THE RESEARCH QUESTION TO WHICH THE VIEW BELONGS TO
research_uri = "http://risis.eu/activity/idea_77f81f"

# THE LINKSETS AND/OR LENSES THAT COMPOSE THE VIEW
# BY DEFAULT OPERATOR FOR A VIEW IS THE INTERSECTION OF THE LENS ELEMENTS
lens_1 = "http://risis.eu/lens/union_Eter_LeidenRanking_P1614043027"
lens_2 = "http://risis.eu/lens/union_Eter_Grid_N312479101"
linkset_5 = "http://risis.eu/linkset/eter_eter_gadm_stat_identity_N307462801"
linkset_6 = "http://risis.eu/linkset/grid_grid_gadm_stat_identity_N627321033"

# THE VIEW SPECIFICATION IS DEFINED BY
#   THE RESEARCH QUESTION
#   THE DATASETS OF INTEREST
view_specs = {
    St.researchQ_URI: research_uri,
    St.datasets: [lens_1, lens_2, linkset_5, linkset_6],
    St.lens_operation: Ns.lensOpi
}

###############################################################################################################
""" DESIGN YOUR VIEW SPECIFICATIONS """
###############################################################################################################

grid_properties = {
    St.graph: "http://risis.eu/dataset/grid",
    St.data: [
        {St.entity_datatype: "http://risis.eu/grid/ontology/class/Institution",
         St.properties: ["http://risis.eu/grid/ontology/predicate/types",
                         "http://risis.eu/grid/ontology/predicate/country",
                         "http://risis.eu/grid/ontology/predicate/city",
                         "http://risis.eu/grid/ontology/predicate/name"]
         }
    ]
}

gridStats_properties = {
    St.graph: "http://risis.eu/dataset/gridStats",
    St.data: [
        {
            St.entity_datatypes: "http://risis.eu/grid/ontology/class/Institution",
            St.properties: ["http://risis.eu//temp-match/temp-match/predicate/hasCode",
                            "http://risis.eu//temp-match/temp-match/predicate/type",
                            "http://risis.eu//temp-match/temp-match/predicate/country",
                            "http://risis.eu//temp-match/temp-match/predicate/city",
                            "http://risis.eu//temp-match/temp-match/predicate/subTotal",
                            "http://risis.eu//temp-match/temp-match/predicate/hasOrgCount"]
         }
    ]
}

grid_gadm_stat_pro = {
    St.graph: "http://risis.eu/dataset/grid_gadm_stat",
    St.data: [
        {
            St.entity_datatypes: "http://risis.eu/grid/ontology/class/Institution",
            St.properties: ["http://risis.eu//temp-match/temp-match/predicate/level",
                            "http://risis.eu//temp-match/temp-match/predicate/typeCount"]
        }
    ]
}

eter_gadm_stat_pro = {
    St.graph: "http://risis.eu/dataset/eter_gadm_stat",
    St.data: [
        {
            St.entity_datatype: "http://risis.eu/eter/ontology/class/University",
            St.properties: ["http://risis.eu//temp-match/temp-match/predicate/level",
                            "http://risis.eu//temp-match/temp-match/predicate/total"]
        }
    ]

}

leiden_properties = {
    St.graph: "http://risis.eu/dataset/leidenRanking",
    St.data: [
        {
            St.entity_datatype: "no_type",
            St.properties: ["http://risis.eu/leidenRanking/ontology/predicate/University",
                            "http://risis.eu/leidenRanking/ontology/predicate/Country",
                            "http://risis.eu/leidenRanking/ontology/predicate/Field",
                            "http://risis.eu/leidenRanking/ontology/predicate/Period",
                            "http://risis.eu/leidenRanking/ontology/predicate/Frac_counting",
                            "http://risis.eu/leidenRanking/ontology/predicate/P",
                            "http://risis.eu/leidenRanking/ontology/predicate/P_top1",
                            "http://risis.eu/leidenRanking/ontology/predicate/PP_top1",
                            "http://risis.eu/leidenRanking/ontology/predicate/P_top10",
                            "http://risis.eu/leidenRanking/ontology/predicate/PP_top10",
                            "http://risis.eu/leidenRanking/ontology/predicate/P_collab",
                            "http://risis.eu/leidenRanking/ontology/predicate/P_int_collab",
                            "http://risis.eu/leidenRanking/ontology/predicate/PP_short_dist_collab",
                            "http://risis.eu/leidenRanking/ontology/predicate/P_long_dist_collab"
                            ]
        }
    ]

}

eter_properties = {
        St.graph: "http://risis.eu/dataset/eter",
        St.data: [
            {
                St.entity_datatype: "http://risis.eu/eter/ontology/class/University",
                St.properties: [("http://risis.eu/eter/ontology/predicate/english_Institution_Name", True),
                                ("http://risis.eu/eter/ontology/predicate/institution_Name", False),
                                ("http://risis.eu/eter/ontology/predicate/country_Code", True),
                                "http://risis.eu/eter/ontology/predicate/institution_Category_English",
                                "http://risis.eu/eter/ontology/predicate/foundation_year",
                                "http://risis.eu/eter/ontology/predicate/university_hospital",
                                "http://risis.eu/eter/ontology/predicate/geographic_coordinates_latitude",
                                "http://risis.eu/eter/ontology/predicate/geographic_coordinates_longitude",
                                "http://risis.eu/eter/ontology/predicate/multisite_institution",
                                "http://risis.eu/eter/ontology/predicate/personnel_expenditure_EURO",
                                "http://risis.eu/eter/ontology/predicate/nonpersonnel_expenditure_EURO",
                                "http://risis.eu/eter/ontology/predicate/nonpersonnel_expenditure_EURO",
                                "http://risis.eu/eter/ontology/predicate/core_budget_EURO",
                                "http://risis.eu/eter/ontology/predicate/third_party_funding_EURO",
                                "http://risis.eu/eter/ontology/predicate/private_funding_EURO",
                                "http://risis.eu/eter/ontology/predicate/student_fees_funding_EURO",
                                "http://risis.eu/eter/ontology/predicate/total_academic_staff_FTE",
                                "http://risis.eu/eter/ontology/predicate/students_enrolled_at_ISCED_6_men",
                                "http://risis.eu/eter/ontology/predicate/students_enrolled_at_ISCED_6_women",
                                "http://risis.eu/eter/ontology/predicate/students_enrolled_at_ISCED_6_foreigner",
                                "http://risis.eu/eter/ontology/predicate/students_enrolled_at_ISCED_7_men",
                                "http://risis.eu/eter/ontology/predicate/students_enrolled_at_ISCED_7_women",
                                "http://risis.eu/eter/ontology/predicate/students_enrolled_at_ISCED_7_foreigner",
                                "http://risis.eu/eter/ontology/predicate/graduates_at_ISCED_8_men",
                                "http://risis.eu/eter/ontology/predicate/graduates_at_ISCED_8_women",
                                "http://risis.eu/eter/ontology/predicate/graduates_at_ISCED_8_foreigner"]
            }
        ]


}

# SPECIAL CASE WHERE THE PROPERTY NAME SPACE....
eter_enriched = {
    St.graph: "http://risis.eu/dataset/eter_orgCountPerAdminLevelInGrid",
    St.data: [
        {
            St.entity_datatype: "http://risis.eu/eter/ontology/class/University",
            St.properties: ["http://risis.eu//temp-match/temp-match/predicate/isIn",
                            ["isIn", "http://risis.eu//temp-match/temp-match/predicate/hasOrgCount"],
                            ["isIn", "http://risis.eu//temp-match/temp-match/predicate/hasCode"]
                            ]
        }
    ]

}

leiden_p = {
    St.graph: "http://risis.eu/dataset/leidenRanking",
    St.data: [
        {
            St.entity_datatype: "http://risis.eu/leidenRanking/ontology/class/University",
            St.properties: [
                "http://risis.eu/leidenRanking/ontology/predicate/P_long_dist_collab"
            ]
        }
    ]
}

view_filter = [grid_gadm_stat_pro, eter_gadm_stat_pro, grid_properties, leiden_properties, eter_properties]


###############################################################################################################
""" EXECUTE VIEW """
###############################################################################################################
# THE SAVE ARGUMENT GIVES THE FREEDOM TO FIRST CHECK HOW THE VIEW LOOKS
#  LIKE BY CHECKING THE TABLE OUTPUT BEFORE DECIDING TO SAVE THE VIEW
#  return {"metadata": view_metadata, "query": query, "table": table}
OUTPUT = view(view_specs, view_filter, save=False, limit=75)

# for key, value in OUTPUT.items():
#     print key, ":\n", value

# PRINT THE RESULT OF THE VIEW QUERY
query = OUTPUT["query"]
# print query

# DISPLAY THE RESULT OF THE VIEW A A TABLE
space = 70 # DETERMINES THE DISTANCE BETWEEN COLUMNS
# display_result( query, info=filter, spacing=space, limit=10, is_activated=True)
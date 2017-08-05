import Alignments.ToRDF.CSV as CSV
""" CONVERTING ORGREF 2017 07 03 """

# convert_1 = CSV.CSV(
#     database="orgref_20170703", is_trig=True, subject_id=10,
#     file_to_convert="E:\Linking2GRID\Data\orgref_20170703\orgref.csv",
#     separator=",", entity_type="Organisation", rdftype=[3])


# convert_2 = CSV.CSV(
#     database="leidenRanking_2015", is_trig=True, subject_id=0,
#     file_to_convert="E:\Linking2GRID\Data\Leiden Ranking 2015 extended\LR_results_all_orgs.txt",
#     separator="\t", entity_type="University", rdftype=[])

# convert_2 = CSV.CSV(
#     database="eter_2014", is_trig=True, subject_id=1,
#     file_to_convert="E:\Linking2GRID\Data\ETER 2017\eter_export_2014.csv",
#     separator=";", entity_type="University", rdftype=[])

# ORGREG ENTITY
convert_2 = CSV.CSV(
    database="orgreg_20170718", is_trig=True, subject_id=0,
    file_to_convert="E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Entities.txt",
    separator=";", entity_type="University", rdftype=[])
import Alignments.ToRDF.CSV as CSV
""" CONVERTING ORGREF 2017 07 03 """

# ORGREF
convert_1 = CSV.CSV(
    database="orgref_20170703", is_trig=True, subject_id=10,
    file_to_convert="E:\Linking2GRID\Data\orgref_20170703\orgref.csv",
    separator=",", entity_type="Organisation", rdftype=[3], activated=False)

# LEIDEN RANKING
convert_2 = CSV.CSV(
    database="leidenRanking_2015", is_trig=True, subject_id=0,
    file_to_convert="E:\Linking2GRID\Data\Leiden Ranking 2015 extended\LR_results_all_orgs.txt",
    separator="\t", entity_type="University", rdftype=[], activated=False)

# ETER
convert_3 = CSV.CSV(
    database="eter_2014", is_trig=True, subject_id=1,
    file_to_convert="E:\Linking2GRID\Data\ETER 2017\eter_export_2014.csv",
    separator=";", entity_type="University", rdftype=[], activated=False)

# >>> ORGREG ENTITY
# =================
entity_path_1 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Entities.txt"
entity_path_2 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005\entity_20171005.txt"
entity_path_3 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005\csv\orgreg_register" \
                "_export_all_20171005__Entities.csv"

convert_4 = CSV.CSV(
    database="orgreg_20170718", is_trig=True, subject_id=0,
    file_to_convert=entity_path_3,
    separator=",", entity_type="University", rdftype=[],  activated=False)

# >>> ORGREG CHARACTERISTICS
# ==========================
characteristics_path_1 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Characteristics.txt"
characteristics_path_2 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005\csv" \
                         "\orgreg_register_export_all_20171005__Characteristics.csv"
convert_5 = CSV.CSV(
    database="orgreg_20170718", is_trig=True, subject_id=1,
    file_to_convert=characteristics_path_2,
    separator=",", entity_type="Characteristics", rdftype=[10, 11],
    embedded_uri=[
        {
            'id': 0,
            'reverse': True,
            'namespace': None,
            'predicate': "characteristicsOf"
        }],  activated=False)

# >>> ORGREG demographic
# =====================
demographic_path_1 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Demographics.txt"
demographic_path_2 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005\csv" \
                     "\orgreg_register_export_all_20171005__Demographics.csv"
parent = {
    'id': 1,
    'reverse': True,
    'namespace': None,
    'predicate': "parentOf"
}
child = {
    'id': 3,
    'reverse': True,
    'namespace': None,
    'predicate': "childOf"
}
convert_6 = CSV.CSV(
    database="orgreg_20170718", is_trig=True, subject_id=0,
    file_to_convert=demographic_path_2,
    separator=",", entity_type="Demographic", rdftype=[], embedded_uri=[parent, child], activated=False)

# >>> ORGREG linkages
# ===================
linkage_path_1 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__Linkages.csv"
linkage_path_2 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005\csv" \
                 "\orgreg_register_export_all_20171005__Linkages.csv"
convert_7 = CSV.CSV(
    database="orgreg_20170718", is_trig=True, subject_id=0,
    file_to_convert=linkage_path_2,
    separator=",", entity_type="Linkages", rdftype=[], embedded_uri=[1, 3], activated=False)

# ORGREG LOCATION
# ===============
location_path_1 = "E:\Linking2GRID\Data\OrgReg 20170718\ORGREG_20170718__LOCATION.txt"
location_path_2 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005\csv" \
                  "\orgreg_register_export_all_20171005__Location.csv"
resource = {
    'id': 0,
    'reverse': True,
    'namespace': None,
    'predicate': "locationOf"}
convert_8 = CSV.CSV(
    database="orgreg_20170718", is_trig=True, subject_id=2,
    file_to_convert=location_path_2,
    separator=",", entity_type="Location", rdftype=[], embedded_uri=[resource], activated=False)


# >>> ORGREG linkages
# ===================
eter_1 = "C:\Users\Al\Google Drive\RISIS-Project-VU\WP 7 - datasets\OrgReg\Orgreg_20171005" \
                 "\orgreg_hei_export5October2017_.csv"

test_path = "C:\Users\Al\Downloads\Atest\orgreg_hei_export5October2017_.csv"

convert_12 = CSV.CSV(
    database="eter20171005", is_trig=True, subject_id=1,
    file_to_convert=eter_1,
    separator=";", entity_type="higher_education", rdftype=[], embedded_uri=None, activated=False)



# convert_10 = CSV.CSV(
#     database="test", is_trig=True, subject_id=0,
#     file_to_convert="C:\Users\Al\Downloads\CSV_Test.csv",
#     separator=",", entity_type="idea", rdftype=[],  activated=False)
#
# convert_11 = CSV.CSV(
#     database="test", is_trig=True, subject_id=0,
#     file_to_convert="C:\Users\Al\Downloads\CSV_Test.csv",
#     separator=",", entity_type="idea", activated=True)
#
# print convert_10

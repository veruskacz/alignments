import Alignments.ToRDF.CSV as CSV
""" CONVERTING ORGREF 2017 07 03 """
convert_2 = CSV.CSV(
    database="orgref_20170703", is_trig=True, subject_id=10,
    file_to_convert="E:\Linking2GRID\Data\orgref_20170703\orgref.csv",
    separator=",", entity_type="Organisation", rdftype=[3])
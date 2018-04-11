# encoding=utf-8

import Alignments.Examples.LinkValidation.Data as Data
import Alignments.UserActivities.Plots as Plt
import Alignments.Examples.LinkValidation.Functions as Functions
from os.path import join
# import cStringIO as Buffer
# import Alignments.UserActivities.Import_Data as Im


net_size = 3
# SET THE MAX SIZE FOR THE NETWORK
net_max_size = 3
# LENS PREFIX
lens_prefix = "http://risis.eu/lens/{}"
# SIZE OF THE CLUSTER TO OUTPUT
greater_equal = False
# THE OUTPUT DIRECTORY FOR CLUSTERS THAT ARE I
# 1. N THE SAME PROXIMITY
# 2. WITH O.7 NAME SIMILARITY THRESHOLD A
# ND AT LEAST ONE NODE IS IN THE NETHERLANDS
directory = "C:\Productivity\LinkAnalysis\ISWC2018\Netherlands_geo"
directory_geo = "C:\Productivity\LinkAnalysis\ISWC2018\Geo_demo_1"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# EXPERIMENT-2: OVERLAP BETWEEN: GRID - ETER - LEIDEN - ORGREG - ORGREG - H2020
# Using APPROXIMATE SIMILARITY
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# THE LENS TO USE FOR NETWORK EXTRACTION
lens50before = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898")
lens50after = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_N287253238")
lens500before = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963")
lens500after = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_N997542894")
lens2000before = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707")
lens2000after = lens_prefix.format("union_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312")


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# PLOT THE GRAPHS TO FILE AND ALSO OUTPUT A TEXT VERSION
# GENERATE AN EVALUATION SHEET
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Plt.cluster_d_test(lens50before, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)

Plt.cluster_d_test(lens500before, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)

Plt.cluster_d_test(lens2000before, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)

Plt.cluster_d_test(lens50after, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)

Plt.cluster_d_test(lens500after, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)

Plt.cluster_d_test(lens2000after, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)


union_50_B = "union_50B_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898"
union_50_A = "union_50A_Eter_2014_Grid_20170712_Orgreg_20170718_N287253238"
union_500_B = "union_500B_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963"
union_500_A = "union_500A_Eter_2014_Grid_20170712_Orgreg_20170718_N997542894"
union_2000_B = "union_2000B_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707"
union_2000_A = "union_2000A_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312"

# GEO NAME NETHERLANDS DIRECTORY
geoname_netherlands = "3_Analysis_20180403\\{}"
set_50_before_nether = join(directory, geoname_netherlands.format(union_50_B))
set_50_after_nether = join(directory, geoname_netherlands.format(union_50_A))
set_500_before_nether = join(directory, geoname_netherlands.format(union_500_B))
set_500_after_nether = join(directory, geoname_netherlands.format(union_500_A))
set_2000_before_nether = join(directory, geoname_netherlands.format(union_2000_B))
set_2000_after_nether = join(directory, geoname_netherlands.format(union_2000_A))

# GEO NAME NETHERLANDS DIRECTORY
geoname = "3_Analysis_20180308\\{}"
set_50_before = join(directory_geo, geoname.format(union_50_B))
set_50_after = join(directory_geo, geoname.format(union_50_A))
set_500_before = join(directory_geo, geoname.format(union_500_B))
set_500_after = join(directory_geo, geoname.format(union_500_A))
set_2000_before = join(directory_geo, geoname.format(union_2000_B))
set_2000_after = join(directory_geo, geoname.format(union_2000_A))


def extract_evaluation_subset(variables, temporal="", save_in="",  file_path_to_extract="", activated=False):
    # GENERATE THE INTERSECTION FILE BETWEEN COMPLETE FILE AND THE NETHERLANDS SUBSET
    variables[0] = Functions.folder_check(variables[1], variables[2], diff_1=False, diff_2=False, save_in=save_in,
                                             intersection=True, tracking=False, track_dir=None, detailed=True,
                                             activated=True)

    # USING THE INTERSECTION FILE, GENERATE THE NETHERLANDS EVALUATION SUBSET
    # "C:\Productivity\LinkAnalysis\ISWC2018\Diff_N1620012972.text"
    file_path_to_extract = "{}\\{}\\{}".format(directory_geo, geoname.format(variables[3]), variables[4])
    Functions.extract_cluster_stats(variables[0], file_path_to_extract,  temporal=temporal, save_in=save_in)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 50 METERS BEFORE                                                                      #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
activate_50 = False
save_in = "C:\Productivity\LinkAnalysis\ISWC2018\PeterValidation_geo_name"

if activate_50 is True:
    var50_before = ["", set_50_before_nether, set_50_before, union_50_B, "3_50m_ClusterSheet_20180308.txt"]
    extract_evaluation_subset(var50_before, temporal="B", save_in=save_in, activated=True)

    var50_after = ["", set_50_after_nether, set_50_after, union_50_A, "3_50m_ClusterSheet_20180308.txt"]
    extract_evaluation_subset(var50_after, temporal="A", save_in=save_in,  activated=True)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 500 METERS BEFORE                                                                      #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
activate_500 = False
save_in = "C:\Productivity\LinkAnalysis\ISWC2018\PeterValidation_geo_name"

if activate_500 is True:

    var500_before = ["", set_500_before_nether, set_500_before, union_500_B, "3_500m_ClusterSheet_20180308.txt"]
    extract_evaluation_subset(var500_before, temporal="B", save_in=save_in, activated=True)

    var500_after = ["", set_500_after_nether, set_500_after, union_500_A, "3_500m_ClusterSheet_20180308.txt"]
    extract_evaluation_subset(var500_after, temporal="A", save_in=save_in,  activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 500 METERS BEFORE                                                                      #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
activate_2000 = True
save_in = "C:\Productivity\LinkAnalysis\ISWC2018\PeterValidation_geo_name"

if activate_2000 is True:

    var2000_before = ["", set_2000_before_nether, set_2000_before, union_2000_B, "3_2000m_ClusterSheet_20180308.txt"]
    extract_evaluation_subset(var2000_before, temporal="B", save_in=save_in, activated=True)

    var2000_after = ["", set_2000_after_nether, set_2000_after, union_2000_A, "3_2000m_ClusterSheet_20180308.txt"]
    extract_evaluation_subset(var2000_after, temporal="A", save_in=save_in,  activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# EVALUATION SHEET SUMMARY                                                              #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""EXAMPLE"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    EVALUATION SHEET SUMMARY FOR: 5_2_ClusterSheet_20180301.txt

    MACHINE         GOOD    14	HUMAN         GOOD     14	TRUE POSITIVE      13	FALSE POSITIVE      1
    MACHINE          BAD     1	HUMAN          BAD      1	PRECISION       0.929	RECALL          0.929
    MACHINE   ACCEPTABLE     0	HUMAN   ACCEPTABLE      0	FALSE NEGATIVE      1	TRUE NEGATIVE       0
    MACHINE    UNCERTAIN     0	HUMAN    UNCERTAIN      0	F MEASURE       0.929
    TOTAL                   15	TOTAL                  15
                       -----------------------------------
                       |        15 GROUND TRUTHS         |
                       -----------------------------------
                       |  GT Positive   |  GT Negative   |
                       |       14       |       1        |
    ---------------------------------------------------------------------------------------------------------
            | Positive | True Positive  | False Positive |      Precision      | False discovery rate (FDR) |
            |          |       13       |       1        |        0.929        |           0.071            |
    PREDICT -------------------------------------------------------------------------------------------------
            | Negative | False Negative | True Negative  | False omission rate | Negative predictive value  |
            |          |       1        |       0        |         1.0         |            0.0             |
    ---------------------------------------------------------------------------------------------------------
                       |     Recall     |    Fall-out    | P. Likelihood Ratio |          F1 score          |
                       |     0.929      |      1.0       |       0.929         |           0.929            |
                       --------------------------------------------------------------------------------------
    Precision = Positive Predicted Value (PPV) = TP (TP + FP)
    Recall = True Positive Rate (TPR) = TP / GT
    False discovery rate (FDR) =  Σ False positive / Σ Predicted condition positive
    Negative predictive value (NPV) =  Σ True negative / Σ Predicted condition negative
    False omission rate (FOR) = Σ False negative / Σ Predicted condition negative
    False positive rate (FPR), Fall-out, probability of false alarm = Σ False positive / Σ Condition negative
    Positive likelihood ratio (LR+) = TPR / FPR
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
check_folder = lens50after
year = "20180301"
for size in range(3, 0):
    doc_path = join(directory, "{0}_Analysis_{1}\{2}\{0}_2_ClusterSheet_{1}.txt".format(size, year, check_folder))

    doc_path1 = join(directory,
                     "Peter - Link Validation Sample\{0}_2_ClusterSheet_{1}.txt".format(size, year))

    doc_path2 = join(directory,
                     "Peter - Link Validation Sample - Corrected\{0}_2_ClusterSheet_{1}.txt".format(size, year))

    Functions.good_bad_count_stats(
        doc_path2, machine_bad=False, human_good=False, machine_good=False,
        machine_acceptable=False, machine_uncertain=False, activated=True)

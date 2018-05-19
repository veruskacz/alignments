# encoding=utf-8


import math
from os.path import join
import Alignments.Examples.LinkValidation.Data as Data
import Alignments.UserActivities.Plots as Plt
import Alignments.Examples.LinkValidation.Functions as Functions
# import cStringIO as Buffer
# import Alignments.UserActivities.Clustering as Cls
# import Alignments.Settings as St
# from os import listdir, system, path  # , startfile
# from Alignments.Utility import normalise_path as nrm
# from os.path import join, isdir, isfile
# import codecs  # , subprocess


def sigmoid(x):
    # return math.exp(x)/ (math.exp(x) + 10)
    return x / float(math.fabs(x) + 1.6)

"""
    Geo_demo_1 is the main experiment
    Geo_demo_2 is about all clusters greater than 2
"""


lens_prefix = "http://risis.eu/lens/{}"
# DEMO-1 CONTAINS ALL CLUSTER SIZES
directory = "C:\Productivity\LinkAnalysis\ISWC2018\Geo_demo_1"
# DEMO-2 CONTAINS DATA FOR CLUSTERS OF SIZE 3
directory_all = "C:\Productivity\LinkAnalysis\ISWC2018\Geo_demo_2"
line = "-------------------------------------------------------------------------------------------"
header = "\n{}\n\t\t{}\n{}"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    THE LINK NETWORK OF 50 METERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
run50 = True
if run50 is True:

    print header.format(line, "THE LINK NETWORK OF 50 METERS", line)

    # """"""""""""""""""""""""""""""""""""""""""""""""
    #     PLOT THE LINK NETWORK OF 50 METERS BEFORE
    #       92 CLUSTERS OF SIZE 3 FOUND
    #       63 CLUSTERS OF SIZE 4 FOUND
    #       16 CLUSTERS OF SIZE 5 FOUND
    # """"""""""""""""""""""""""""""""""""""""""""""""

    lens50before = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898")
    Plt.cluster_d_test(lens50before, network_size=3,  network_size_max=0,
                       targets=Data.targets, constraint_targets=None, constraint_text=None,
                       directory=directory, greater_equal=False, limit=None, only_good=False, activated=True)

    # """"""""""""""""""""""""""""""""""""""""""""""""
    #     PLOT THE LINK NETWORK OF 50 METERS AFTER
    #       31 CLUSTERS OF SIZE 3 FOUND
    #       04 CLUSTERS OF SIZE 4 FOUND
    #       00 CLUSTERS OF SIZE 5 FOUND
    # """"""""""""""""""""""""""""""""""""""""""""""""

    lens50after = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_N287253238")
    Plt.cluster_d_test(lens50after, network_size=3,  network_size_max=0,
                       targets=Data.targets, constraint_targets=None, constraint_text=None,
                       directory=directory, greater_equal=False, limit=None, only_good=False, activated=True)

    # """""""""""""""""""""""""""""""""""""""""""""
    #     INVESTIGATION 01 : COMPARE CLUSTERS
    # """""""""""""""""""""""""""""""""""""""""""""

    set_50BEFORE = join(directory, "3_Analysis_20180308\union_50B_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898")
    set_50AFTER = join(directory, "3_Analysis_20180308\union_50A_Eter_2014_Grid_20170712_Orgreg_20170718_N287253238")
    Functions.folder_check(set_50BEFORE, set_50AFTER, diff_1=True, diff_2=True, intersection=True,
                           tracking=False, track_dir=directory, detailed=False, activated=False)

    # COMPUTE FOR CLUSTERS >= 3 BEFORE
    set_50BEFORE = join(
        directory_all, "3_Analysis_20180308\union_50B_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898")
    Functions.folder_check(set_50BEFORE, set_50BEFORE, diff_1=False, diff_2=False, intersection=True,
                           tracking=False, track_dir=directory_all, detailed=False, activated=False)

    # COMPUTE FOR CLUSTERS >= 3 AFTER
    set_50AFTER = join(
        directory_all, "3_Analysis_20180308\union_50A_Eter_2014_Grid_20170712_Orgreg_20170718_N287253238")
    Functions.folder_check(set_50AFTER, set_50AFTER, diff_1=False, diff_2=False, intersection=True,
                           tracking=False, track_dir=directory_all, detailed=False, activated=False)

    # """""""""""""""""""""""""""""""""""""""""""""
    #        EVALUATION SHEET SUMMARY
    # """""""""""""""""""""""""""""""""""""""""""""
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

    # FAILED
    # from_

    size = 3
    year = "20180308"
    check_folder_b = "union_50B_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898"
    check_folder_a = "union_50A_Eter_2014_Grid_20170712_Orgreg_20170718_N287253238"
    for size in range(3, 4):

        print "\n>>> PASS ---------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory, "{0}_Analysis_{1}\{2}\\{0}diff_50m_ClusterSheet_{1}.txt".format(size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=False, activated=True)

        # Functions.confusion_matrix(
        #     true_p=21, false_p=0, true_n=1, false_n=9, ground_truth_p=30, observations=31, confusion=False)

        print "\n>>> FAILED -------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory, "{0}_Analysis_{1}\{2}\\Failed{0}diff_50m_ClusterSheet_{1}.txt".format(
                size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=False, activated=True)

        print "\n>>> BEFORE -------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory, "{0}_Analysis_{1}\{2}\\{0}_50m_ClusterSheet_{1}.txt".format(
                size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)

        print "\n>>> AFTER --------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory, "{0}_Analysis_{1}\{2}\\{0}_50m_ClusterSheet_{1}.txt".format(
                size, year, check_folder_a))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    THE LINK NETWORK OF 500 METERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
run500 = False
if run500 is True:

    print header.format(line, "THE LINK NETWORK OF 500 METERS", line)
    # """"""""""""""""""""""""""""""""""""""""""""""""
    #     PLOT THE LINK NETWORK OF 500 METERS BEFORE
    #       249 CLUSTERS OF SIZE 3 FOUND
    #       141 CLUSTERS OF SIZE 4 FOUND
    #       076 CLUSTERS OF SIZE 5 FOUND
    # """"""""""""""""""""""""""""""""""""""""""""""""
    lens500before = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963")
    Plt.cluster_d_test(lens500before, network_size=3,  network_size_max=0,
                       targets=Data.targets, constraint_targets=None, constraint_text=None,
                       directory=directory, greater_equal=False, limit=None, only_good=False, activated=True)

    # """"""""""""""""""""""""""""""""""""""""""""""""
    #     PLOT THE LINK NETWORK OF 50 METERS AFTER
    #       155 CLUSTERS OF SIZE 3 FOUND
    #       008 CLUSTERS OF SIZE 4 FOUND
    #       002 CLUSTERS OF SIZE 5 FOUND
    # """"""""""""""""""""""""""""""""""""""""""""""""
    lens500after = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_N997542894")
    Plt.cluster_d_test(lens500after, network_size=3,  network_size_max=0,
                       targets=Data.targets, constraint_targets=None, constraint_text=None,
                       directory=directory, greater_equal=False, limit=None, only_good=False, activated=True)

    # """""""""""""""""""""""""""""""""""""""""""""
    #     INVESTIGATION 02 : COMPARE CLUSTERS
    # """""""""""""""""""""""""""""""""""""""""""""

    set_500BEFORE = join(
        directory, "3_Analysis_20180308\union_500B_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963")
    set_500AFTER = join(directory, "3_Analysis_20180308\union_500A_Eter_2014_Grid_20170712_Orgreg_20170718_N997542894")
    Functions.folder_check(set_500BEFORE, set_500AFTER, diff_1=True, diff_2=True, intersection=True,
                           tracking=False, track_dir=directory, detailed=False, activated=False)

    # COMPUTE FOR CLUSTERS >= 3 BEFORE
    set_500BEFORE = join(
        directory_all, "3_Analysis_20180308\union_500B_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963")
    Functions.folder_check(set_500BEFORE, set_500BEFORE, diff_1=False, diff_2=False, intersection=True,
                           tracking=False, track_dir=directory_all, detailed=False, activated=False)

    # COMPUTE FOR CLUSTERS >= 3 AFTER
    set_500AFTER = join(
        directory_all, "3_Analysis_20180308\union_500A_Eter_2014_Grid_20170712_Orgreg_20170718_N997542894")
    Functions.folder_check(set_500AFTER, set_500AFTER, diff_1=False, diff_2=False, intersection=True,
                           tracking=False, track_dir=directory_all, detailed=False, activated=False)

    # """""""""""""""""""""""""""""""""""""""""""""
    #        EVALUATION SHEET SUMMARY
    # """""""""""""""""""""""""""""""""""""""""""""
    size = 3
    year = "20180308"
    check_folder_b = "union_500B_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963"
    check_folder_a = "union_500A_Eter_2014_Grid_20170712_Orgreg_20170718_N997542894"
    for size in range(3, 4):

        print "\n>>> PASS ---------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(directory, "{0}_Analysis_{1}\{2}\\{0}diff_500m_ClusterSheet_{1}.txt".format(
            size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=False, activated=True)

        print "\n>>> FAILED -------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(directory, "{0}_Analysis_{1}\{2}\\Failed{0}diff_500m_ClusterSheet_{1}.txt".format(
            size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=False, activated=True)

        print "\n>>> BEFORE -------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(directory, "{0}_Analysis_{1}\{2}\\{0}_500m_ClusterSheet_{1}.txt".format(
            size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)

        print "\n>>> AFTER --------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(directory, "{0}_Analysis_{1}\{2}\\{0}_500m_ClusterSheet_{1}.txt".format(
            size, year, check_folder_a))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    THE LINK NETWORK OF 2000 METERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
run2000 = False
if run2000 is True:

    print header.format(line, "THE LINK NETWORK OF 2000 METERS", line)

    # """"""""""""""""""""""""""""""""""""""""""""""""
    #     PLOT THE LINK NETWORK OF 500 METERS BEFORE
    #       198 CLUSTERS OF SIZE 3 FOUND
    #       129 CLUSTERS OF SIZE 4 FOUND
    #       084 CLUSTERS OF SIZE 5 FOUND
    # """"""""""""""""""""""""""""""""""""""""""""""""
    lens2000before = lens_prefix.format("union_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707")
    Plt.cluster_d_test(lens2000before, network_size=3,  network_size_max=0,
                       targets=Data.targets, constraint_targets=None, constraint_text=None,
                       directory=directory, greater_equal=False, limit=None, only_good=False, activated=True)

    # """"""""""""""""""""""""""""""""""""""""""""""""
    #     PLOT THE LINK NETWORK OF 50 METERS AFTER
    #       342 CLUSTERS OF SIZE 3 FOUND
    #       016 CLUSTERS OF SIZE 4 FOUND
    #       006 CLUSTERS OF SIZE 5 FOUND
    # """"""""""""""""""""""""""""""""""""""""""""""""
    lens2000after = lens_prefix.format("union_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312")
    Plt.cluster_d_test(lens2000after, network_size=3,  network_size_max=0,
                       targets=Data.targets, constraint_targets=None, constraint_text=None,
                       directory=directory, greater_equal=False, limit=None, only_good=False, activated=True)

    # """""""""""""""""""""""""""""""""""""""""""""
    #     INVESTIGATION 01 : COMPARE CLUSTERS
    # """""""""""""""""""""""""""""""""""""""""""""
    # set_500BEFORE = join(
    #     directory, "3_Analysis_20180308\union_500B_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963")
    set_2000BEFORE = join(
        directory, "3_Analysis_20180308\union_2000B_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707")
    set_2000AFTER = join(
        directory, "3_Analysis_20180308\union_2000A_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312")
    Functions.folder_check(set_2000BEFORE, set_2000AFTER, diff_1=True, diff_2=True, intersection=True,
                           tracking=False, track_dir=directory, detailed=False, activated=False)

    # COMPUTE FOR CLUSTERS >= 3 BEFORE
    set_2000BEFORE = join(
        directory, "3_Analysis_20180308\union_2000B_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707")
    Functions.folder_check(set_2000BEFORE, set_2000BEFORE, diff_1=False, diff_2=False, intersection=True,
                           tracking=False, track_dir=directory_all, detailed=False, activated=False)

    # COMPUTE FOR CLUSTERS >= 3 AFTER
    set_2000AFTER = join(
        directory, "3_Analysis_20180308\union_2000A_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312")
    Functions.folder_check(set_2000AFTER, set_2000AFTER, diff_1=False, diff_2=False, intersection=True,
                           tracking=False, track_dir=directory_all, detailed=True, activated=False)

    # """""""""""""""""""""""""""""""""""""""""""""
    #        EVALUATION SHEET SUMMARY
    # """""""""""""""""""""""""""""""""""""""""""""
    size = 3
    year = "20180308"
    check_folder_b = "union_2000B_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707"
    check_folder_a = "union_2000A_Orgreg_20170718_Eter_2014_Grid_20170712_N1471387312"
    for size in range(3, 4):

        print "\n>>> PASS ---------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory, "{0}_Analysis_{1}\{2}\\{0}diff_2000m_ClusterSheet_{1}.txt".format(size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=False, activated=True)

        print "\n>>> FAILED -------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory,
            "{0}_Analysis_{1}\{2}\\Failed{0}diff_2000m_ClusterSheet_{1}.txt".format(size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=False, activated=True)

        print "\n>>> BEFORE -------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory,
            "{0}_Analysis_{1}\{2}\\{0}_2000m_ClusterSheet_{1}.txt".format(size, year, check_folder_b))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)

        print "\n>>> AFTER --------------------------------------------------------------------------------------------"
        print "------------------------------------------------------------------------------------------------------"
        doc_path = join(
            directory,
            "{0}_Analysis_{1}\{2}\\{0}_2000m_ClusterSheet_{1}.txt".format(size, year, check_folder_a))
        Functions.good_bad_count_stats(
            doc_path, machine_bad=False, human_good=False, machine_good=False,
            machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    EXTRACTING THE DIFFERENCE(BEFORE - AFTER) A.K.A FAILED & THE INTERSECTION(BEFORE, AFTER) AKA PASSED
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
before = False
diff = False
if diff is True:

    failed = "Failed" if before is True else ""

    route50r = "C:\Productivity\LinkAnalysis\Geo_demo_1\\{}50RemainingBefore.txt".format(failed)
    route50 = "C:\Productivity\LinkAnalysis\Geo_demo_1\\3_Analysis_20180308\\" \
              "union_50B_Eter_2014_Grid_20170712_Orgreg_20170718_P1611822898\\3_50m_ClusterSheet_20180308.txt"

    route500r = "C:\Productivity\LinkAnalysis\Geo_demo_1\\{}500RemainingBefore.txt".format(failed)
    route500 = "C:\Productivity\LinkAnalysis\Geo_demo_1\\3_Analysis_20180308\\" \
               "union_500B_Eter_2014_Grid_20170712_Orgreg_20170718_N1668834963\\3_500m_ClusterSheet_20180308.txt"

    route2000r = "C:\Productivity\LinkAnalysis\Geo_demo_1\\{}2000RemainingBefore.txt".format(failed)
    route2000 = "C:\Productivity\LinkAnalysis\Geo_demo_1\\3_Analysis_20180308\\" \
                "union_2000B_Eter_2014_Grid_20170712_Orgreg_20170718_P210872707\\3_2000m_ClusterSheet_20180308.txt"

    Functions.extract_cluster_stats(route50r, route50)
    # Functions.extract_cluster_stats(route500r, route500)
    # Functions.extract_cluster_stats(route2000r, route2000)

# Functions.confusion_matrix(t
# rue_p=322, false_p=20, true_n=0, false_n=0, ground_truth_p=322, observations=342, latex=False)

# Functions.confusion_matrix(
# true_p=35, false_p=31, true_n=0, false_n=0, ground_truth_p=35, observations=66, latex=False)

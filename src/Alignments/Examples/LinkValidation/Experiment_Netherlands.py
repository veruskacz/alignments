# encoding=utf-8

import Alignments.Examples.LinkValidation.Data as Data
import Alignments.UserActivities.Plots as Plt
import Alignments.Examples.LinkValidation.Functions as Functions
from os.path import join
# import cStringIO as Buffer
# import Alignments.UserActivities.Import_Data as Im


net_size = 3
net_max_size = 2


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# EXPERIMENT-2: OVERLAP BETWEEN: GRID - ETER - LEIDEN - ORGREG - ORGREG - H2020
# Using APPROXIMATE SIMILARITY
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# SIZE OF THE CLUSTER TO OUTPUT
greater_equal = False

# THE OUTPUT DIRECTORY
directory = "C:\Productivity\LinkAnalysis\ISWC2018\Netherlands_name"

# THE LENS TO USE FOR NETWORK EXTRACTION
lens = "union_Eter_2014_LeidenRanking_2015_Grid_20170712_H2020_Orgref_20170703_Orgreg_20170718_P1768695787"
union = "http://risis.eu/lens/{}".format(lens)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# PLOT THE GRAPHS TO FILE AND ALSO OUTPUT A TEXT VERSION
# GENERATE AN EVALUATION SHEET
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Plt.cluster_d_test(union, network_size=net_size,  network_size_max=net_max_size,
                   targets=Data.targets, constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory=directory, greater_equal=greater_equal, limit=None, activated=False)


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
check_folder = lens
year = "20180301"
for size in range(3, 11):
    doc_path = join(directory, "{0}_Analysis_{1}\{2}\{0}_2_ClusterSheet_{1}.txt".format(size, year, check_folder))

    doc_path1 = join(directory,
                     "Peter - Link Validation Sample\{0}_2_ClusterSheet_{1}.txt".format(size, year))

    doc_path2 = join(directory,
                     "Peter - Link Validation Sample - Corrected\{0}_2_ClusterSheet_{1}.txt".format(size, year))

    Functions.good_bad_count_stats(
        doc_path2, machine_bad=False, human_good=False, machine_good=False,
        machine_acceptable=False, machine_uncertain=False, latex=True, activated=True)

import Alignments.Examples.LinkValidation.Data as Data
import Alignments.UserActivities.Plots as Plt
import Alignments.Examples.LinkValidation.Functions as Functions
from os.path import join
import cStringIO as Buffer
# import Alignments.UserActivities.Import_Data as Im


net_size = 2
net_max_size = 2


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# EXPERIMENT-2: OVERLAP BETWEEN: GRID - ETER - LEIDEN - ORGREG - ORGREG - H2020
# Using APPROXIMATE SIMILARITY
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# RESEARCH QUESTION LABEL   : Link Validation Reprocess 0.75
# RESEARCH QUESTION ID      : http://risis.eu/activity/idea_3944ec
test = "APPROXIMATE-TRIAL-3"

# SIZE OF THE CLUSTER TO OUTPUT
greater_equal = False

# THE OUTPUT DIRECTORY
directory_1 = "C:\Productivity\LinkAnalysis\ISWC2018\{}-00".format(test)
directory_2 = "C:\Productivity\LinkAnalysis\ISWC2018\{}-3".format(test)

# THE LENS TO USE FOR NETWORK EXTRACTION
lens = "union_Eter_2014_LeidenRanking_2015_Grid_20170712_H2020_Orgref_20170703_Orgreg_20170718_P1768695787"
union = "http://risis.eu/lens/{}".format(lens)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# PLOT THE GRAPHS TO FILE AND ALSO OUTPUT A TEXT VERSION
# GENERATE AN EVALUATION SHEET
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Plt.cluster_d_test(union, network_size=net_size,  network_size_max=net_max_size, targets=Data.targets,
                   constraint_targets=Data.targets_constraints, constraint_text="NL, Netherlands",
                   directory="", greater_equal=greater_equal, limit=None, activated=False)


Plt.cluster_d_test(union, network_size=net_size,  network_size_max=net_max_size, targets=None,
                   constraint_targets=None, constraint_text="",
                   directory="", greater_equal=greater_equal, limit=None, activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# EVALUATION SHEET SUMMARY [CONFUSION MATRIX]                                           #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
check_folder = lens
year = "20180216"
for size in range(5, 11):
    doc_path = join(directory_1, "{0}_Analysis_{1}\{2}\{0}_ClusterSheet_{1}.txt".format(size, year, check_folder))
    Functions.good_bad_count_stats(
        doc_path, machine_bad=False, human_good=False, machine_good=False,
        machine_acceptable=False, machine_uncertain=False, latex=True, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# GET STATISTICS ON NETWORK EVALUATION IN TERMS OF GOOD/ACCEPTABLE - BAD AND UNDECIDABLE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# size = 9
# check_folder = lens
# year = "20180216"
# year_2 = "20180204"
# set_0 = join(directory_1, "{}_Analysis_{}\{}".format(size, year, check_folder))
# set_1 = join(directory_2, "{}_Analysis_{}\{}".format(size, year_2, check_folder))
#
# # USE EVALUATION SHEET SUMMARY FOR PLOTS
# doc_path = join(directory_1, "{0}_Analysis_{1}\{2}\{0}_ClusterSheet_20180216.txt".format(size, year, check_folder))
# plot_dict = Functions.good_bad_count_stats(doc_path, machine_bad=False, machine_good=False, machine_acceptable=False,
#                                            machine_uncertain=False, human_good=False, activated=False)
#
# Functions.folder_check(set_0, set_0, diff_1=True, intersection=True, tracking=True,
#                        track_dir=directory_1, plot_dict=plot_dict, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# IT DISPLAYS THE FIGURES USING INPUT PROMPT. TO CONTINUE, ENTER YES, Y OR 1
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# size = 6
# year = "20180202"
# investigation_folder_path = join(
#     directory_1, "{0}_Analysis_{1}\{2}".format(size, year, lens))
# Functions.investigate(investigation_folder_path, directory_1, activated=False)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# DISAMBIGUATING A SET OF RESOURCES                                                     #
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# import Alignments.UserActivities.Clustering as cls
# source = ["http://risis.eu/orgref_20170703/resource/31111149", "http://risis.eu/orgref_20170703/resource/28890185",
# 	"http://www.grid.ac/institutes/grid.415000.0", 	"http://www.grid.ac/institutes/grid.413203.7",
# 	"http://www.grid.ac/institutes/grid.439850.3", "http://risis.eu/orgref_20170703/resource/14577019"]
# print cls.disambiguate_network_2( source, Data.targets )


# 3 ==> GOOD 2099/2522 BAD 423/2522 UNCERTAIN 0/2522
# 4 ==> GOOD 453/832 BAD 234/832 UNCERTAIN 145/832
# 5 ==>
# 6 ==> GOOD 126/229 BAD 59/229 UNCERTAIN 44/229
#       GOOD 128/229 BAD 59/229 UNCERTAIN 42/229
#       GOOD 127/229 BAD 59/229 UNCERTAIN 43/229

# 7 ==> GOOD 9/124 BAD 33/124 UNCERTAIN 82/124
# 8 ==>
# 9 ==>
#  N995150116


print "STATS"
sheet_builder = Buffer.StringIO()
for i in range(3, 0):
    print "\nITERATION {}".format(i)
    text = Plt.cluster_d_test_stats(union, network_size=i,  targets=Data.targets,
                                    directory=None, greater_equal=greater_equal, limit=None, activated=False)
    sheet_builder.write("{}\n".format(text))

# print sheet_builder.getvalue()


# print "OPEN AIRE LINK NETWORK STATS"
# sheet_builder = Buffer.StringIO()
# for i in range(3, 100):
#     print "\nITERATION {}".format(i)
#     text = Plt.cluster_d_test_stats(lens, network_size=i,  targets=Data.targets_openaire,
#                                     directory=None, greater_equal=greater_equal, limit=None, activated=False)
#     sheet_builder.write("{}\n".format(text))
# print sheet_builder.getvalue()

import Alignments.Examples.LinkValidation.Data as Data
import Alignments.UserActivities.Plots as Plt
import Alignments.Examples.LinkValidation.Functions as Functions
from os.path import join

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# EXPERIMENT-2: OVERLAP BETWEEN: GRID - ETER - LEIDEN - ORGREG - ORGREG - H2020
# Compute
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# SIZE OF THE CLUSTER TO OUTPUT
greater_equal = False

# THE OUTPUT DIRECTORY
directory = "C:\Productivity\LinkAnalysis\TRIAL-2"
directory_2 = "C:\Productivity\LinkAnalysis\TRIAL-5"

# THE LENS TO USE FOR NETWORK EXTRACTION
lens = "union_LeidenRanking_2015_Grid_20170712_Orgref_20170703_Orgreg_20170718_Eter_2014_H2020_P1908729565"
union = "http://risis.eu/lens/{}".format(lens)

# PLOT THE GRAPHS TO FILE AND ALSO OUTPUT A TEXT VERSION
# GENERATE AN EVALUATION SHEET
for i in range(7, 8):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union, network_size=i,  targets=Data.targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)

# GET STATISTICS ON NETWORK EVALUATION IN TERMS OF GOOD/ACCEPTABLE - BAD AND UNDECIDABLE
size = 6
year = "20180206"
year_2 = "20180204"
check_folder = lens
set_0 = join(directory, "{}_Analysis_{}\{}".format(size, year, check_folder))
set_1 = join(directory_2, "{}_Analysis_{}\{}".format(size, year_2, check_folder))
Functions.folder_check(set_0, set_0, diff_1=True, intersection=True,
                       tracking=True, track_dir=directory, activated=False)

# IT DISPLAYS THE FIGURES USING INPUT PROMPT. TO CONTINUE, ENTER YES, Y OR 1
size = 6
year = "20180202"
investigation_folder_path = join(directory, "{}_Analysis_{}\{}".format(size, year, lens))
Functions.investigate(investigation_folder_path, directory, activated=False)

# ----------------------------------#
# DISAMBIGUATING A SET OF RESOURCES #
# ---------------------------------_#
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
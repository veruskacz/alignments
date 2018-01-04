import Alignments.UserActivities.Plots as Plt
import Alignments.UserActivities.Clustering as Cls
import Alignments.Settings as St
from os import listdir, system, startfile
from Alignments.Utility import normalise_path as nrm
from os.path import join, isdir, isfile
import codecs, subprocess
import _winreg as winreg


linkset_1 = "http://risis.eu/linkset/clustered_exactStrSim_N167245093"
linkset_2 = "http://risis.eu/linkset/clustered_exactStrSim_N1245679810818748702"
linkset_3 = "http://risis.eu/linkset/clustered_test"
resources_list = ["<http://risis.eu/orgref_20170703/resource/1389122>",
                  "<http://risis.eu/cordisH2020/resource/participant_993809912>",
                  "<http://www.grid.ac/institutes/grid.1034.6>"]

# print disambiguate_network(linkset_1, resources_list)
# Cls.cluster_d_test(linkset_4, network_size=3,  directory="C:\Users\Al\Videos\LinkMetric",
#                    greater_equal=True, limit=50000)

linkset = "http://risis.eu/linkset/clustered_exactStrSim_N1245679810818748702"
org = "http://risis.eu/orgreg_20170718/resource/organization"
uni = "http://risis.eu/orgreg_20170718/ontology/class/University"
ds = "http://risis.eu/dataset/orgreg_20170718"
# resources_matched(alignment=linkset, dataset=ds, resource_type=uni, matched=True)

# THE INITIAL DATASET IS grid_20170712
grid_GRAPH = "http://risis.eu/dataset/grid_20170712"
grid_org_type = "http://xmlns.com/foaf/0.1/Organization"
grid_cluster_PROPS = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
                      "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]
grid_link_org_props = ["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2004/02/skos/core#prefLabel",
                       "http://www.w3.org/2004/02/skos/core#altLabel",
                       "http://xmlns.com/foaf/0.1/homepage",
                       "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>",
                       "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>"]
grid_main_dict = {St.graph: grid_GRAPH,
                  St.data: [{St.entity_datatype: grid_org_type, St.properties: grid_link_org_props}]}

# [ETER] DATASET TO ADD
eter_GRAPH = "http://risis.eu/dataset/eter_2014"
eter_cluster_PROPS = ["http://risis.eu/eter_2014/ontology/predicate/Country_Code"]
eter_org_type = "http://risis.eu/eter_2014/ontology/class/University"
eter_link_org_props = ["http://risis.eu/eter_2014/ontology/predicate/Institution_Name",
                       "<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
                       "http://risis.eu/eter_2014/ontology/predicate/Name_of_foreign_institution",
                       "http://risis.eu/eter_2014/ontology/predicate/Institutional_website",
                       "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__longitude",
                       "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__latitude"]
eter_main_dict = {St.graph: eter_GRAPH,
                  St.data: [{St.entity_datatype: eter_org_type, St.properties: eter_link_org_props}]}

# [ORGREG] DATASET TO ADD
orgreg_GRAPH = "http://risis.eu/dataset/orgreg_20170718"
orgreg_cluster_PROPS = ["<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>"
                        "/<http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_location>",
                        "http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment"]
orgreg_org_type = "http://risis.eu/orgreg_20170718/resource/organization"
orgreg_link_org_props = ["http://risis.eu/orgreg_20170718/ontology/predicate/Name_of_entity",
                         "http://risis.eu/orgreg_20170718/ontology/predicate/English_name_of_entity",
                         "http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English",
                         "http://risis.eu/orgreg_20170718/ontology/predicate/Website_of_entity",
                         "<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>"
                         "/<http://risis.eu/orgreg_20170718/ontology/predicate/Geographical_coordinates__latitude>",
                         "<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>"
                         "/<http://risis.eu/orgreg_20170718/ontology/predicate/Geographical_coordinates__longitude>"]

orgreg_main_dict = {St.graph: orgreg_GRAPH,
                    St.data: [{St.entity_datatype: orgreg_org_type, St.properties: orgreg_link_org_props}]}

targets = [
    grid_main_dict,
    orgreg_main_dict,
    eter_main_dict
]

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    TEST FUNCTIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def folder_check(file_1, file_2, diff_1=False, diff_2=False, intersection=False,
                 tracking=None, track_dir=None, activated=False):

    if activated is False:
        return None

    folders_1 = [f for f in listdir(nrm(file_1)) if isdir(join(nrm(file_1), f))]
    folders_2 = [f for f in listdir(nrm(file_2)) if isdir(join(nrm(file_2), f))]
    print "\nPATH 1: {}".format(len(folders_1))
    print "PATH : {}".format(len(folders_2))
    set_1 = set(folders_1)
    set_2 = set(folders_2)

    # Dynamically get path to AcroRD32.exe
    # acro_read = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')


    if diff_1 is True:
        diff = set_1 - set_2
        print "\nDIFF(FOLDER_1 [{}] - FOLDER_2 [{}]) [{}]".format(len(folders_1) -1,  len(folders_2) -1, len(diff))
        count = 0
        for item in diff:
            count += 1
            print "\t>>> {}".format(item)
            target = join(nrm(file_1), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            # OPEN THE PDF FROM DEFAULT READER
            # target_path2 = join(nrm(target), doc2[0])
            # system(target_path2)
            # startfile(target_path2)

            # OPEN WITH ADOBE
            # cmd = '{0} /N /T "{1}" ""'.format(acro_read, target_path2)
            # print "PRINTING PDF"
            # subprocess.Popen(cmd)


            # reading = open(target_path2)
            # print reading.read()
            if doc and tracking is True:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                node = read.readline().strip()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)

    if diff_2 is True:
        diff = set_2 - set_1
        print "\nDIFF(FOLDER_2 - FOLDER_1) [{}]".format(len(diff))
        for item in diff:
            print "\t{}".format(item)

    if intersection is True:
        diff = set_1.intersection(set_2)
        print "\nINTERSECTION(FOLDER_1 [{}] - FOLDER_2 [{}]) [{}]".format(
            len(folders_1) -1, len(folders_2) -1, len(diff))
        for item in diff:
            print "\t{}".format(item)


def track(directory, resource, activated=False):

    if activated is False:
        return None

    print "\nMAIN DIRECTORY {}".format(directory)
    # LOOK FOR MAIN FOLDERS IN MAIN DIRECTORY
    main_folders = [f for f in listdir(nrm(directory)) if isdir(join(nrm(directory), f))]

    # GO THROUGH EACH MAIN FOLDER
    for main_folder in main_folders:
        main_path = join(directory, main_folder)
        # print "\tMAIN-FOLDER: {}".format(main_folder)
        # FOREACH MAIN FOLDER GAT THE SUB-FOLDER
        sub_folders = [f for f in listdir(nrm(main_path)) if isdir(join(nrm(main_path), f))]

        for sub_folder in sub_folders:
            sub_path = join(main_path, sub_folder)
            # print "\t\tSUB-FOLDER: {}".format(sub_folder)

            # TARGET FOLDERS
            target_folder = [f for f in listdir(nrm(sub_path)) if isdir(join(nrm(sub_path), f))]
            for target in target_folder:
                i_folder = "{}".format(join(main_path, sub_path, target))
                # print "\t\t\tTARGET-FOLDER: {}".format(target)
                i_file = [f for f in listdir(nrm(i_folder)) if isfile(join(nrm(i_folder), f))]


                for target_file in i_file:
                    if target_file.lower().endswith(".txt"):
                        target_path = join(main_path, sub_path, target, target_file)
                        wr = codecs.open(target_path, "rb")
                        text = wr.read()
                        wr.close()

                        result = text.__contains__(resource)
                        if result is True:
                            print "\n\tMAIN-FOLDER: {}".format(main_folder)
                            print "\t\tSUB-FOLDER: {}".format(sub_folder)
                            print "\t\t\tTARGET-FOLDER: {}".format(target)
                            print "\t\t\t\tTARGET FILE: {}".format(target_file)
                            target = join(main_path, sub_path, target)
                            print "\tPATH: {}".format(target)

                            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]
                            trg_path = join(nrm(target), doc[0])
                            system(trg_path)
                            print "\t\t\t\t{}".format(result)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    COMPUTING AN ALIGNMENT STATISTICS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# OUTPUT FALSE RETURNS THE MATRIX WHILE OUTPUT TRUE RETURNS THE DISPLAY MATRIX IN A TABLE FORMAT
stats = Cls.resource_stat(alignment=linkset, dataset=ds, resource_type=org, output=True, activated=False)
# for stat in stats:
#     for key, value in stat.items():
#         print "{:21} : {}".format(key, value)

# Cls.disambiguate_network_2(["<http://www.grid.ac/institutes/grid.474119.e>",
#                             "<http://risis.eu/orgreg_20170718/resource/HR1016>",
#                             "<http://www.grid.ac/institutes/grid.4808.4>"], targets, output=True)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    PLOT THE LINK NETWORK
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
size = 7
ls_4 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N1655042445"
ls_5 = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069"
ls_1k = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_P1640316176"
ls_app = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_N1942436340"
ls_app_50m = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_P571882700"
# GEO-SIMILARITY OF NEARBY 1 KILOMETER
# REFINED BY EXACT MATCHED
# ==> UNION OF SIX LINKSETS
union = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_P1476302481"
directory = "C:\Users\Al\Videos\LinkMetric\Test-2"

Plt.cluster_d_test(ls_app_50m, network_size=3,  targets=targets,
                   directory=directory, greater_equal=False, limit=70000, activated=False)

directory = "C:\Users\Al\Videos\LinkMetric\Test-3"
Plt.cluster_d_test(union, network_size=3,  targets=targets,
                   directory=directory, greater_equal=False, limit=70000, activated=False)

track(directory, "Academy of Fine Arts Vienna", activated=False)

# for i in range(3, 50):
#
#     size = i
#
#     Plt.cluster_d_test(ls_4, network_size=size,  targets=targets,
#                        directory=directory, greater_equal=False, limit=70000, activated=True)
#
#     Plt.cluster_d_test(ls_5, network_size=size,  targets=targets,
#                        directory=directory, greater_equal=False, limit=70000, activated=True)
#
#     Plt.cluster_d_test(ls_1k, network_size=size,  targets=targets,
#                        directory=directory, greater_equal=False, limit=70000, activated=True)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ANALYSING THE LINKED NETWORK FILES TEST-1
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
TEST_1 = "C:\Users\Al\Videos\LinkMetric\Test-1"
# CLUSTER USING NEARBY 50 METERS
set_1 = join(TEST_1, "4_Analysis_20171225\union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069")
# CLUSTER USING NEARBY 100 METERS
set_2 = join(TEST_1, "4_Analysis_20171225\union_Grid_20170712_Eter_2014_Orgreg_20170718_N1655042445")
# CLUSTER USING NEARBY 1000 METERS
set_3 = join(TEST_1, "3_Analysis_20171225\union_Eter_2014_Orgreg_20170718_Grid_20170712_P1640316176")
# CLUSTER USING NEARBY 1000 METERS and EXACT
set_4 = join(TEST_1, "3_Analysis_20171225\union_Eter_2014_Orgreg_20170718_Grid_20170712_P1476302481")
# LOOKING AT CLUSTERS THAT EVOLVED AS THE MATCHING METHOD LOOSENS UP
# THE SET DIFFERENCE REVEALS THAT 26 CLUSTERS OF SIZE 3 EVOLVED
folder_check(set_1, set_2, diff_1=True, tracking=True, track_dir=TEST_1, activated=False)
# TRACKING THE CLUSTERS THAT EVOLVED
# track(directory, track_3)
folder_check(set_4, set_1, diff_1=True, tracking=True, track_dir=TEST_1, activated=True)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ANALYSING THE LINKED NETWORK FILES TEST-2
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# t50 = "C:\Users\Al\Videos\LinkMetric\7_Analysis_20171215\union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069"
# t100 = "C:\Users\Al\Videos\LinkMetric\7_Analysis_20171215\union_Grid_20170712_Eter_2014_Orgreg_20170718_N1655042445"
# t1000 = "C:\Users\Al\Videos\LinkMetric\7_Analysis_20171215\union_Eter_2014_Orgreg_20170718_Grid_20170712_P1640316176"
t50 = "C:\Users\Al\Videos\LinkMetric\Test-2\\3_Analysis_20171229\union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069"
t100 = "C:\Users\Al\Videos\LinkMetric\Test-2\\3_Analysis_20171229\union_Grid_20170712_Eter_2014_Orgreg_20170718_N1655042445"
t1000 = "C:\Users\Al\Videos\LinkMetric\Test-2\\3_Analysis_20171229\union_Eter_2014_Orgreg_20170718_Grid_20170712_P1640316176"
app = "C:\Users\Al\Videos\LinkMetric\Test-2\\3_Analysis_20171229\union_Eter_2014_Orgreg_20170718_Grid_20170712_N1942436340"
U_ap_50 = "C:\Users\Al\Videos\LinkMetric\Test-2\3_Analysis_20171229\union_Grid_20170712_Eter_2014_Orgreg_20170718_P571882700"


# wr = codecs.open("C:\Users\Al\Videos\LinkMetric\\"
#                  "7_Analysis_20171220\union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069\\"
#                  "7_N2141339763\cluster_N2141339763_20171220.txt", "rb")
# text = wr.read()
# print text.__contains__("<http://www.grid.ac/institutes/grid.457417.4>")
# wr.close()
# print "DOE!"

# main folder
#   Sub-Folders
#       target folders
#           Target file
#               Comparison

track_3 = "<http://risis.eu/eter_2014/resource/HU0023>"
track_5 = "<http://www.grid.ac/institutes/grid.469502.c>"
# track(directory, "<http://risis.eu/eter_2014/resource/FR0088>")
# track(directory, "<http://www.grid.ac/institutes/grid.452199.2>")

folder_check(t50, t100)
folder_check(t50, t1000)
directory = "C:\Users\Al\Videos\LinkMetric\Test-1"
# folder_check(t50, app, True)
folder_check(app, t50)
folder_check(U_ap_50, t50)
track(directory, track_3)
print "DONE!!!"
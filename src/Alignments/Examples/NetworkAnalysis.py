# encoding=utf-8
import  math

def sigmoid(x):
    # return math.exp(x)/ (math.exp(x) + 10)
    return x / float(math.fabs(x) + 1.6)


import cStringIO as Buffer
import Alignments.UserActivities.Plots as Plt
import Alignments.UserActivities.Clustering as Cls
import Alignments.Settings as St
from os import listdir, system, path  # , startfile
from Alignments.Utility import normalise_path as nrm
from os.path import join, isdir, isfile
import codecs  # , subprocess
# import _winreg as winreg
# node = int(raw_input("\n\tNODES?\t"))
# v = int(raw_input("\n\tEDGES?\t"))
# d = int(raw_input("\n\tDIAMETER?\t"))
# b = int(raw_input("\n\tBRIDGE?\t"))



# b = 1
# d = 3
# v = 7
# node = 6


b = 4
d = 4
v = 4
node = 5
# ==> 0.32 / 0.35


# max_connectivity = node - 1
# max = node*(node - 1)/2
# nc = 1 - (v/float(max))
# nb = b / float(node -1)
# nd = (d - 1)/float (node - 2)
# quality = float(nc + nb + nd)/3
# quality2 = float(nd * nc + nb)/2
# quality3 = (1*math.pow(2,b)/math.pow(2,d) + nc) / float(2)
# print "MAX: {}\nCLOSURE: {}\nBRIDGE: {}\nDIAMETER: {}\nQUALITY: {} {} {}".format(
#     max, nc, nb, nd, quality, quality2, quality3)


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

    keyword = "\tQUALITY USED"
    set_a = set([])
    set_b = set([])
    folders_1 = []
    folders_2 = []

    if path.isdir(file_1):
        folders_1 = [f for f in listdir(nrm(file_1)) if isdir(join(nrm(file_1), f))]
        set_a = set(folders_1)

    if path.isdir(file_2):
        folders_2 = [f for f in listdir(nrm(file_2)) if isdir(join(nrm(file_2), f))]
        set_b = set(folders_2)

    print "\nPATH 1: {}".format(len(folders_1))
    print "PATH : {}".format(len(folders_2))

    # Dynamically get path to AcroRD32.exe
    # acro_read = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, 'Software\\Adobe\\Acrobat\Exe')

    if diff_1 is True:
        diff = set_a - set_b
        print "\nDIFF(FOLDER_1 [{}] - FOLDER_2 [{}]) = [{}]".format(len(folders_1),  len(folders_2), len(diff))
        count = 0
        good = 0
        bad = 0
        uncertain = 0
        for item in diff:
            count += 1
            output = "\t>>> {}".format(item)
            target = join(nrm(file_1), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]

            if doc:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:
                    node = read.readline()
                    if len(node) == 0:
                        break
                    if node.startswith(keyword):
                        value = float(node.replace(keyword, "").replace(":", "").strip())
                        if value <= 0.1:
                            good +=1
                            output = "{:<22}{:12}\t{}".format(output, "GOOD", value)
                        elif value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}\t{}".format(output, "BAD", value)
                            break
                        elif value > 0.1 and value < 0.25:
                            uncertain += 1
                            output = "{:<22}{:12}\t{}".format(output, "UNDECIDED",  value)
                read.close()
            print output

            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

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
                for i in range(0, 6):
                    node = read.readline().strip()
                read.close()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)

        print "GOOD {0}/{3} BAD {1}/{3} UNCERTAIN {2}/{3}".format(good, bad, uncertain, len(diff))

    if diff_2 is True:
        count = 0
        good = 0
        bad = 0
        uncertain = 0
        diff = set_b - set_a
        print "\nDIFF(FOLDER_2 [{}] - FOLDER_1 [{}]) = [{}]".format(len(folders_2), len(folders_1), len(diff))
        for item in diff:
            count += 1
            output = "\t>>> {}".format(item)
            target = join(nrm(file_2), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            if doc:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:
                    node = read.readline()
                    if len(node) == 0:
                        break
                    if node.startswith(keyword):
                        value = float(node.replace(keyword, "").replace(":", "").strip())
                        if value <= 0.1:
                            good +=1
                            output = "{:<22}{:12}\t{}".format(output, "GOOD", value)
                        elif value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}\t{}".format(output, "BAD", value)
                            break
                        elif value > 0.1 and value < 0.25:
                            uncertain += 1
                            output = "{:<22}{:12}\t{}".format(output, "UNDECIDED",  value)
                read.close()
            print output

            if doc and tracking is True:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                for i in range(0, 6):
                    node = read.readline().strip()
                read.close()
                print "\t{}-TRACKING {}".  format(count, node)
                track(directory=track_dir, resource=node, activated=activated)
                next_step = raw_input("\n\tCONTINUE?\t")
                if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                    continue
                else:
                    exit(0)
        print "GOOD {0}/{3} BAD {1}/{3} UNCERTAIN {2}/{3}".format(good, bad, uncertain, len(diff))

    if intersection is True:
        diff = set_a.intersection(set_b)
        print "\nINTERSECTION(FOLDER_1 [{}] - FOLDER_2 [{}]) [{}]".format(
            len(folders_1), len(folders_2), len(diff))
        good = 0
        bad = 0
        uncertain = 0
        for item in diff:
            output = "\t>>> {}".format(item)
            target = join(nrm(file_2), item)
            doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
            # doc2 = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

            if doc:
                target_path = join(nrm(target), doc[0])
                read = open(target_path)
                while True:
                    node = read.readline()
                    if len(node) == 0:
                        break
                    if node.startswith(keyword):
                        value = float(node.replace(keyword, "").replace(":", "").strip())
                        if value <= 0.1:
                            good +=1
                            output = "{:<22}{:12}\t{}".format(output, "GOOD", value)
                        elif value >= 0.25:
                            bad += 1
                            output = "{:<22}{:12}\t{}".format(output, "BAD", value)
                            break
                        elif value > 0.1 and value < 0.25:
                            uncertain += 1
                            output = "{:<22}{:12}\t{}".format(output, "UNDECIDED",  value)
                read.close()
            print output
        print "GOOD {0}/{3} BAD {1}/{3} UNCERTAIN {2}/{3}".format(good, bad, uncertain, len(diff))

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

                            pdf = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]
                            txt = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
                            trg_path = join(nrm(target), pdf[0])
                            txt_path = join(nrm(target), txt[0])
                            system(trg_path)
                            # system(txt_path)
                            # print "\t\t\t\t{}".format(result)


def investigate(target_directory, track_directory=None, activated=False):

    if activated is False:
        return None

    folders = [f for f in listdir(nrm(target_directory)) if isdir(join(nrm(target_directory), f))]
    print "\nINVESTIGATING NO: {}".format(len(folders))
    count = 0
    for item in folders:
        count += 1
        print "\t>>> {}".format(item)
        target = join(nrm(target_directory), item)
        doc = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.txt')]
        pdf = [f for f in listdir(nrm(target)) if join(nrm(target), f).endswith('.pdf')]

        if doc and pdf:
            doc_path = join(nrm(target), doc[0])

            read = open(doc_path)
            node= ""
            for i in range(0,6):
                node = read.readline().strip()

            if track_directory and path.isdir(track_directory):
                print "\t{}-TRACKING {}".format(count, node)
                track(directory=track_directory, resource=node, activated=activated)
                # system(doc_path)
            elif pdf:
                pdf_path = join(nrm(target), pdf[0])
                system(pdf_path)
                # system(doc_path)

            next_step = raw_input("\tCONTINUE?\t")
            print ""
            if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
                continue
            else:
                exit(0)


def generate_eval_sheet(alignment, network_size, greater_equal=True, targets=None,):
    # RUN THE CLUSTER
    count = 0
    tabs = "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"
    a_builder = Buffer.StringIO()
    a_builder.write("Count	ID					STRUCTURE	E-STRUCTURE-SIZE	NETWORK QUALITY		REFERENCE\n")
    clusters_0 = Cls.links_clustering(alignment, None)
    for i_cluster in clusters_0.items():
        children = i_cluster[1][St.children]
        check = len(children) >= network_size if greater_equal else len(children) == network_size
        first = False
        if check:
            count += 1

            # 2: FETCHING THE CORRESPONDENTS
            smallest_hash = float('inf')
            for child in children:
                hashed = hash(child)
                if hashed <= smallest_hash:
                    smallest_hash = hashed
            test(count, smallest_hash, a_builder, alignment, children)
            # # MAKE SURE THE FILE NAME OF THE CLUSTER IS ALWAYS THE SAME
            # smallest_hash = "{}".format(str(smallest_hash).replace("-", "N")) if str(
            #     smallest_hash).startswith("-") \
            #     else "P{}".format(smallest_hash)
            #
            # a_builder.write("\n{:5}\t{:20}{:12}{:20}{:20}".format(count, smallest_hash, "", "", ""))
            # if targets is None:
            #     a_builder.write(Cls.disambiguate_network(alignment, children))
            # else:
            #     response = Cls.disambiguate_network_2(children, targets, output=False)
            #     if response:
            #         temp = ""
            #         dataset = ""
            #         # for line in response:
            #         #     print line
            #
            #         for i in range(1, len(response)):
            #             if i == 1:
            #                 temp = response[i][1]
            #
            #             elif dataset == response[i][0]:
            #                 temp = "{} | {}".format(temp, response[i][1])
            #
            #
            #             else:
            #                 if first is False:
            #                     a_builder.write("{}\n".format(temp))
            #                 else:
            #                     a_builder.write( "{:80}{}\n".format("", temp))
            #                 first = True
            #                 temp = response[i][1]
            #
            #
            #             dataset = response[i][0]
            #         a_builder.write( "{:80}{}\n".format("", temp))

    print a_builder.getvalue()
            # next_step = raw_input("\tCONTINUE?\t")
            # if next_step.lower() == "yes" or next_step.lower() == "y" or next_step.lower() == "1":
            #     continue
            # else:
            #     exit(0)

investigate("C:\Users\Al\Videos\LinkMetric\TRIAL-2\3_Analysis_20180111"
            "\union_Grid_20170712_Eter_2014_Orgreg_20170718_P1310881121", "C:\Users\Al\Videos\LinkMetric\TRIAL-2",
            activated=False)


def test(count, smallest_hash, a_builder, alignment, children):
    first = False
    a_builder.write("\n{:<5}\t{:<20}{:12}{:20}{:20}".format(count, smallest_hash, "", "", ""))
    if targets is None:
        a_builder.write(Cls.disambiguate_network(alignment, children))
    else:
        response = Cls.disambiguate_network_2(children, targets, output=False)
        if response:
            temp = ""
            dataset = ""
            # for line in response:
            #     print line

            for i in range(1, len(response)):
                if i == 1:
                    temp = response[i][1]

                elif dataset == response[i][0]:
                    temp = "{} | {}".format(temp, response[i][1])

                else:
                    if first is False:
                        a_builder.write("{}\n".format(temp))
                    else:
                        a_builder.write("{:80}{}\n".format("", temp))
                    first = True
                    temp = response[i][1]

                dataset = response[i][0]
            a_builder.write("{:80}{}\n".format("", temp))


# generate_eval_sheet("http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_P1310881121", network_size=3,
#                     greater_equal=False, targets=targets)

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
directory = "C:\Users\Al\Videos\LinkMetric\Test-2"

Plt.cluster_d_test(ls_app_50m, network_size=3,  targets=targets,
                   directory=directory, greater_equal=False, limit=70000, activated=False)

# # GEO-SIMILARITY OF NEARBY [1 KILOMETER]
# # REFINED BY EXACT MATCHED
# # ==> UNION OF 8 LINKSETS
# union_03 = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_P1476302481"
# directory = "C:\Users\Al\Videos\LinkMetric\Test-3"
# Plt.cluster_d_test(union_03, network_size=3,  targets=targets,
#                    directory=directory, greater_equal=False, limit=70000, activated=False)
# track(directory, "Academy of Fine Arts Vienna", activated=False)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# RUN 00: GEO-SIMILARITY OF NEARBY [50 meters BEFORE]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# ==> UNION OF 8 LINKSETS
# 93 clusters of size 3
# 62 clusters of size 4
# 16 clusters of size 5
# 17 clusters of size 6
# 08 clusters of size 7
# 08 clusters of size 8
# 03 clusters of size 9
# 02 clusters of size 10
greater_equal = False
directory = "C:\Users\Al\Videos\LinkMetric\TRIAL-5"
union_00 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_P451472011"
union_01 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_P1310881121"

track(directory, "C.D.A. College", activated=False)

for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union_00, network_size=i,  targets=targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)

# GEO-SIMILARITY OF NEARBY [50 meters]
# REFINED BY REFINED MATCHED
# ==> UNION OF 8 LINKSETS
# 29 clusters of size 3
# 6 clusters of size 4
# 16 clusters of size 5
# 17 clusters of size 6
# directory = "C:\Users\Al\Videos\LinkMetric\TRIAL-2"
track(directory, "Policejní akademie České republiky v Praze", activated=False)
for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union_01, network_size=i,  targets=targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
RUN 02: GEO-SIMILARITY OF NEARBY [500 meters]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# GEO-SIMILARITY OF NEARBY [100 meters]
# REFINED BY REFINED MATCHED
# ==> UNION OF 8 LINKSETS
# 155 CLUSTERS of size 3
# 010 clusters of size 4
# 002 clusters of size 5
# 004 clusters of size 6
# union_02 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N545709154"
union_021 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N747654693"
union_022 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N758253463"

# directory = "C:\Users\Al\Videos\LinkMetric\TRIAL-2"
track(directory, "Policejní akademie České republiky v Praze", activated=False)

for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union_021, network_size=i,  targets=targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)

for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union_022, network_size=i,  targets=targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)

# LOOKING AT CLUSTERS THAT EVOLVED AS THE MATCHING METHOD LOOSENS UP
# THE SET DIFFERENCE REVEALS THAT 26 CLUSTERS OF SIZE 3 EVOLVED


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
RUN 03: GEO-SIMILARITY OF NEARBY [2 KILOMETER]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# GEO-SIMILARITY OF NEARBY [1 KILOMETER]
# REFINED BY REFINED MATCHED
# ==> UNION OF 8 LINKSETS
# 350 CLUSTERS of size 3
# 018 clusters of size 4
# 004 clusters of size 5
# 007 clusters of size 6
# union_03 = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_P2072038799"
# BEFORE
union_031 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N1996365419"
# AFTER
union_032 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N162258616"

# directory = "C:\Users\Al\Videos\LinkMetric\TRIAL-2"
track(directory, "Vilentum Hogeschool", activated=False)
for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union_031, network_size=i,  targets=targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)

for i in range(3, 0):
    print "\nITERATION {}".format(i)
    Plt.cluster_d_test(union_032, network_size=i,  targets=targets,
                       directory=directory, greater_equal=greater_equal, limit=None, activated=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    INVESTIGATION 01 : COMPARE CLUSTERS FORM 50 METERS TO THOSE OF 100 METERS AND 1 KILOMETER
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ANALYSIS_01 = "C:\Users\Al\Videos\LinkMetric\LinkAnalysis_01"
# CLUSTER USING NEARBY 50 METERS
set_01 = join(ANALYSIS_01, "3_Analysis_20180109union_Grid_20170712_Eter_2014_Orgreg_20170718_P1310881121")
# CLUSTER USING NEARBY 100 METERS
set_02 = join(ANALYSIS_01, "3_Analysis_20180109\union_Grid_20170712_Eter_2014_Orgreg_20170718_N758253463")
# CLUSTER USING NEARBY 1000 METERS
set_03 = join(ANALYSIS_01, "3_Analysis_20180109\union_Grid_20170712_Eter_2014_Orgreg_20170718_N162258616")
# COMPARE CLUSTERS STEMMED FROM NEARBY 50 TO THOSE STEMMED FROM NEARBY 100
folder_check(set_01, set_02, diff_2=True, intersection=True, tracking=True, track_dir=ANALYSIS_01, activated=False)
# COMPARE CLUSTERS STEMMED FROM NEARBY 50 TO THOSE STEMMED FROM NEARBY 1000
folder_check(set_01, set_03, diff_1=True, tracking=True, track_dir=ANALYSIS_01, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ANALYSING THE LINKED NETWORK FILES TEST-1
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

SIZE = 5
TEST_1 = "C:\Users\Al\Videos\LinkMetric\TRIAL-5\\"

# CLUSTER USING NEARBY 50 METERS BEFORE
set_0 = join(TEST_1, "{}_Analysis_20180120\union_Grid_20170712_Eter_2014_Orgreg_20170718_P451472011".format(SIZE))
# CLUSTER USING NEARBY 50 METERS AFTER
set_1 = join(TEST_1, "{}_Analysis_20180120\union_Grid_20170712_Eter_2014_Orgreg_20170718_P1310881121".format(SIZE))

# CLUSTER USING NEARBY 500 METERS BEFORE
set_2 = join(TEST_1, "{}_Analysis_20180120\union_Grid_20170712_Eter_2014_Orgreg_20170718_N747654693".format(SIZE))
# CLUSTER USING NEARBY 500 METERS AFTER
set_3 = join(TEST_1, "{}_Analysis_20180120\union_Grid_20170712_Eter_2014_Orgreg_20170718_N758253463".format(SIZE))

# CLUSTER USING NEARBY 1000 METERS and EXACT
set_4 = join(TEST_1, "{}_Analysis_20180120\union_Grid_20170712_Eter_2014_Orgreg_20170718_N1996365419".format(SIZE))
set_5 = join(TEST_1, "{}_Analysis_20180120\union_Grid_20170712_Eter_2014_Orgreg_20170718_N162258616".format(SIZE))
# LOOKING AT CLUSTERS THAT EVOLVED AS THE MATCHING METHOD LOOSENS UP
# THE SET DIFFERENCE REVEALS THAT 26 CLUSTERS OF SIZE 3 EVOLVED
folder_check(set_0, set_1, diff_1=True, intersection=True, tracking=False, track_dir=directory, activated=True)
print "\n**************************************************************\n"
folder_check(set_2, set_3, diff_1=True, intersection=True, tracking=False, track_dir=directory, activated=True)
print "\n**************************************************************\n"
folder_check(set_4, set_5, diff_1=True, intersection=True, tracking=False, track_dir=directory, activated=True)
# TRACKING THE CLUSTERS THAT EVOLVED
# track(directory, track_3)
folder_check(set_4, set_1, diff_2=True, tracking=True, track_dir=TEST_1, activated=False)

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
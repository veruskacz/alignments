import Alignments.UserActivities.Clustering as Cls
import Alignments.Settings as St
import Alignments.Query as Qry

linkset_1 = "http://risis.eu/linkset/clustered_exactStrSim_N167245093"
linkset_2 = "http://risis.eu/linkset/clustered_exactStrSim_N1245679810818748702"
linkset_3 = "http://risis.eu/linkset/clustered_test"
ls_4 = "http://risis.eu/lens/union_Grid_20170712_Eter_2014_Orgreg_20170718_N1655042445"
ls_5 = "http://risis.eu/lens/union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069"

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

# OUTPUT FALSE RETURNS THE MATRIX WHILE OUTPUT TRUE RETURNS THE DISPLAY MATRIX IN A TABLE FORMAT
stats = Cls.resource_stat(alignment=linkset, dataset=ds, resource_type=org, output=True)
# for stat in stats:
#     for key, value in stat.items():
#         print "{:21} : {}".format(key, value)
exit(0)

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

# Cls.disambiguate_network_2(["<http://www.grid.ac/institutes/grid.474119.e>",
#                             "<http://risis.eu/orgreg_20170718/resource/HR1016>",
#                             "<http://www.grid.ac/institutes/grid.4808.4>"], targets, output=True)
size = 7
directory = "C:\Users\Al\Videos\LinkMetric"
# Cls.cluster_d_test(ls_4, network_size=size,  targets=targets, directory=directory, greater_equal=False, limit=70000)
# Cls.cluster_d_test(ls_5, network_size=size,  targets=targets, directory=directory, greater_equal=False, limit=70000)


from os import listdir
from Alignments.Utility import normalise_path as nPath

from os.path import isfile, join, isdir


path_1 = "C:\Users\Al\Videos\LinkMetric\7_Analysis_20171215\union_Eter_2014_Orgreg_20170718_Grid_20170712_N2030153069"
path_2 = "C:\Users\Al\Videos\LinkMetric\7_Analysis_20171215\union_Grid_20170712_Eter_2014_Orgreg_20170718_N1655042445"
folders_1 = [f for f in listdir(nPath(path_1)) if isdir(join(nPath(path_1), f))]
folders_2 = [f for f in listdir(nPath(path_2)) if isdir(join(nPath(path_2), f))]
print len(folders_1)
print len(folders_2)
diff = set(folders_1) - set(folders_2)
for item in diff:
    print item

print "\n"

diff = set(folders_2) - set(folders_1)
for item in diff:
    print item

print "\n"

diff = set(folders_2).intersection(set(folders_1))
for item in diff:
    print item
# print len(diff)


# encoding=utf-8

import Alignments.Settings as St
import Alignments.Utility as Ut

linkset_1 = "http://risis.eu/linkset/clustered_exactStrSim_N167245093"
linkset_2 = "http://risis.eu/linkset/clustered_exactStrSim_N1245679810818748702"
linkset_3 = "http://risis.eu/linkset/clustered_test"
resources_list = ["<http://risis.eu/orgref_20170703/resource/1389122>",
                  "<http://risis.eu/cordisH2020/resource/participant_993809912>",
                  "<http://www.grid.ac/institutes/grid.1034.6>"]

linkset = "http://risis.eu/linkset/clustered_exactStrSim_N1245679810818748702"
org = "http://risis.eu/orgreg_20170718/resource/organization"
uni = "http://risis.eu/orgreg_20170718/ontology/class/University"
ds = "http://risis.eu/dataset/orgreg_20170718"


# 1. THE INITIAL DATASET IS grid_20170712
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

# 2. [ETER] DATASET TO ADD
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

# 3. [ORGREG] DATASET TO ADD
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

# 4. [ORGREF] DATASET TO ADD
orgref_GRAPH = "http://risis.eu/dataset/orgref_20170703"
orgref_org_type = "http://risis.eu/orgref_20170703/ontology/class/Organisation"
orgref_link_org_props = ["http://risis.eu/orgref_20170703/ontology/predicate/Name",
                         "http://risis.eu/orgref_20170703/ontology/predicate/Website",
                         "http://risis.eu/orgref_20170703/ontology/predicate/Wikidata",
                         "http://risis.eu/orgref_20170703/ontology/predicate/Wikipedia"]
orgref_main_dict = {St.graph: orgref_GRAPH,
                    St.data: [{St.entity_datatype: orgref_org_type, St.properties: orgref_link_org_props}]}


# 5. [LEIDEN] DATASET TO ADD
leiden_GRAPH = "http://risis.eu/dataset/leidenRanking_2015"
leiden_org_type = "http://risis.eu/leidenRanking_2015/ontology/class/University"
leiden_link_org_props = ["http://risis.eu/leidenRanking_2015/ontology/predicate/actor"]
leiden_main_dict = {St.graph: leiden_GRAPH,
                    St.data: [{St.entity_datatype: leiden_org_type, St.properties: leiden_link_org_props}]}

# 4. [H2020] DATASET TO ADD
h2020_GRAPH = "http://risis.eu/dataset/h2020"
h2020_org_type = "http://xmlns.com/foaf/0.1/Organization"
h2020_link_org_props = ["http://xmlns.com/foaf/0.1/name", "http://xmlns.com/foaf/0.1/page"]
h2020_main_dict = {St.graph: h2020_GRAPH,
                   St.data: [{St.entity_datatype: h2020_org_type, St.properties: h2020_link_org_props}]}

# 4. [H2020] DATASET TO ADD
openaire_GRAPH = "http://risis.eu/dataset/openAire_20180219"
openaire_org_type = "http://lod.openaire.eu/vocab/OrganizationEntity"
openaire_link_org_props = ["http://lod.openaire.eu/vocab/countryName", "http://lod.openaire.eu/vocab/prefLabel",
                           "http://lod.openaire.eu/vocab/organizationWebsite"]
openaire_main_dict = {St.graph: openaire_GRAPH,
                      St.data: [{St.entity_datatype: openaire_org_type, St.properties: openaire_link_org_props}]}

targets = [
    grid_main_dict,
    orgreg_main_dict,
    eter_main_dict,
    orgref_main_dict,
    leiden_main_dict,
    h2020_main_dict
]

targets_openaire = [
    grid_main_dict,
    orgref_main_dict,
    h2020_main_dict,
    openaire_main_dict
]


grid_constraint_PROPS = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"]
eter_constraint_PROPS = ["http://risis.eu/eter_2014/ontology/predicate/Country_Code"]
orgref_constraint_PROPS = ["http://risis.eu/orgref_20170703/ontology/predicate/Country"]
openaire_constraint_PROPS = ["http://lod.openaire.eu/vocab/countryCode", " http://lod.openaire.eu/vocab/countryName"]


orgreg_constraint_PROPS = ["<http://risis.eu/orgreg_20170718/ontology/predicate/locationOf>"
                        "/<http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_location>",
                        "http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment"]

leiden_constraint_PROPS = ["http://risis.eu/leidenRanking_2015/ontology/predicate/country"] # COUNTRY NAME
h2020_constraint_PROPS = ["http://risis.eu/cordisH2020/vocab/country"]



grid_main_dict = {St.graph: grid_GRAPH,
                  St.data: [{St.entity_datatype: grid_org_type, St.properties: grid_constraint_PROPS}]}
eter_main_dict = {St.graph: eter_GRAPH,
                  St.data: [{St.entity_datatype: eter_org_type, St.properties: eter_constraint_PROPS}]}
orgreg_main_dict = {St.graph: orgreg_GRAPH,
                    St.data: [{St.entity_datatype: orgreg_org_type, St.properties: orgreg_constraint_PROPS}]}
orgref_main_dict = {St.graph: orgref_GRAPH,
                    St.data: [{St.entity_datatype: orgref_org_type, St.properties: orgref_constraint_PROPS}]}
leiden_main_dict = {St.graph: leiden_GRAPH,
                    St.data: [{St.entity_datatype: leiden_org_type, St.properties: leiden_constraint_PROPS}]}
h2020_main_dict = {St.graph: h2020_GRAPH,
                   St.data: [{St.entity_datatype: h2020_org_type, St.properties: h2020_constraint_PROPS}]}
openaire_main_dict = {St.graph: openaire_GRAPH,
                      St.data: [{St.entity_datatype: openaire_org_type, St.properties: grid_constraint_PROPS}]}

targets_constraints = [ grid_main_dict, eter_main_dict, orgref_main_dict,
                        orgref_main_dict,  h2020_main_dict, openaire_main_dict]

# print Ut.get_resource_value("http:resources\\al", targets)
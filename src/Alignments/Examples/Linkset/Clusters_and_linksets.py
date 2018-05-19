import Alignments.ConstraintClustering.DatasetsResourceClustering as Dcs
import Alignments.Settings as St
import Alignments.Linksets.SPA_Linkset as Linkset
import Alignments.Utility as Ut


###################################################
# CREATING MULTIPLE CLUSTERS IN ONE STEP
###################################################

# THE INITIAL DATASET IS grid_20170712
grid_GRAPH = "http://risis.eu/dataset/grid_20170712"
grid_org_type = "http://xmlns.com/foaf/0.1/Organization"
grid_cluster_PROPS = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
                      "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]
grid_link_org_props = ["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2004/02/skos/core#prefLabel",
                       "http://www.w3.org/2004/02/skos/core#altLabel",
                       "http://xmlns.com/foaf/0.1/homepage"]
grid_main_dict = {St.graph: grid_GRAPH,
                  St.data: [{St.entity_datatype: grid_org_type, St.properties: grid_link_org_props}]}

# [ORGREF] DATASET TO ADD
orgref_GRAPH = "http://risis.eu/dataset/orgref_20170703"
orgref_cluster_PROPS = ["http://risis.eu/orgref_20170703/ontology/predicate/Country"]
orgref_org_type = "http://risis.eu/orgref_20170703/ontology/class/Organisation"
orgref_link_org_props = ["http://risis.eu/orgref_20170703/ontology/predicate/Name",
                         "http://risis.eu/orgref_20170703/ontology/predicate/Website"]
orgref_main_dict = {St.graph: orgref_GRAPH,
                    St.data: [{St.entity_datatype: orgref_org_type, St.properties: orgref_link_org_props}]}

# [ETER] DATASET TO ADD
eter_GRAPH = "http://risis.eu/dataset/eter_2014"
eter_cluster_PROPS = ["http://risis.eu/eter_2014/ontology/predicate/Country_Code"]
eter_org_type = "http://risis.eu/eter_2014/ontology/class/University"
eter_link_org_props = ["http://risis.eu/eter_2014/ontology/predicate/Institution_Name",
                       "<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
                       "http://risis.eu/eter_2014/ontology/predicate/Name_of_foreign_institution",
                       "http://risis.eu/eter_2014/ontology/predicate/Institutional_website"]
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
                         "http://risis.eu/orgreg_20170718/ontology/predicate/Website_of_entity"]
orgreg_main_dict = {St.graph: orgreg_GRAPH,
                    St.data: [{St.entity_datatype: orgreg_org_type, St.properties: orgreg_link_org_props}]}

# [LEIDEN] DATASET TO ADD
leiden_GRAPH = "http://risis.eu/dataset/leidenRanking_2015"
leiden_cluster_PROPS = ["<http://risis.eu/leidenRanking_2015/ontology/predicate/country>"]
leiden_org_type = "http://risis.eu/leidenRanking_2015/ontology/class/University"
leiden_link_org_props = ["http://risis.eu/leidenRanking_2015/ontology/predicate/actor"]
leiden_main_dict = {St.graph: leiden_GRAPH,
                    St.data: [{St.entity_datatype: leiden_org_type, St.properties: leiden_link_org_props}]}

# [H2020] DATASET TO ADD
h2020_GRAPH = "http://risis.eu/dataset/h2020"
h2020_cluster_PROPS = ["http://risis.eu/cordisH2020/vocab/country"]
h2020_org_type = "http://xmlns.com/foaf/0.1/Organization"
h2020_link_org_props = ["http://xmlns.com/foaf/0.1/name", "http://xmlns.com/foaf/0.1/page"]
h2020_main_dict = {St.graph: h2020_GRAPH,
                   St.data: [{St.entity_datatype: h2020_org_type, St.properties: h2020_link_org_props}]}

# [OPENAIRE] DATASET TO ADD
openaire_GRAPH = "http://risis.eu/dataset/openAire_20170816"
openaire_cluster_PROPS = ["http://dbpedia.org/ontology/country"]
openaire_org_type = "http://xmlns.com/foaf/0.1/Organization"
openaire_link_org_props = ["http://www.w3.org/2004/02/skos/core#prefLabel",
                           "http://www.w3.org/2004/02/skos/core#altLabel",
                           "http://lod.openaire.eu/vocab/webSiteUrl"]
openaire_main_dict = {St.graph: openaire_GRAPH,
                      St.data: [{St.entity_datatype: openaire_org_type, St.properties: openaire_link_org_props}]}

# builder = Dcs.property_builder(grid_link_org_props, "resource_1", "obj_1")
# for item in builder:
#     print item
# exit(0)

targets = [
    grid_main_dict,
    orgref_main_dict,
    orgreg_main_dict,
    eter_main_dict,
    leiden_main_dict,
    h2020_main_dict,
    openaire_main_dict
]

specs = {St.reference: "http://risis.eu/cluster/reference/N1528759258",
         St.mechanism: "exactStrSim",
         St.researchQ_URI: "http://risis.eu/activity/idea_749ab8",
         St.targets: targets}

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 1. [CREATE] A GROUP OF CLUSTERS USING THE [GRID] DATASET AND
    [COUNTRY CODE] AND [COUNTRY NAME] AS CLUSTER CONSTRAINTS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "1. INITIAL GROUP OF CLUSTERS"
response = Dcs.create_clusters(
    initial_dataset_uri=grid_GRAPH, property_uri=grid_cluster_PROPS, strong=True, activated=False)
# reference = response["reference"]
# print reference

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 2. [ADD] NEW RESOURCES TO THE GROUP OF CLUSTERS CREATED AT STEP ONE
    USING THE [ORGREF] DATASET AND [COUNTRY CODE] AS THE CONDITION TO
    BELONG TO AN EXISTING CLUSTER.
    IF A NON EXISTING CLUSTER EXISTS IN [ORGREF] BUT NOT IN THE EXISTING
    GROUP, A NEW CLUSTER IS GENERATED AND ADDED TO THE GROUP.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

reference_2 = "http://risis.eu/cluster/reference/N1528759258"

print "\n2.1 ADDING [ORGREF] RESOURCES TO THE INITIAL GROUP OF CLUSTER"
Dcs.add_to_clusters(reference=reference_2, dataset_uri=orgref_GRAPH, property_uri=orgref_cluster_PROPS, activated=False)

print "\n2.2 ADDING [ETER] RESOURCES TO THE INITIAL GROUP OF CLUSTER"
Dcs.add_to_clusters(reference=reference_2, dataset_uri=eter_GRAPH, property_uri=eter_cluster_PROPS, activated=False)

print "\n2.3 ADDING [LEIDEN] RESOURCES TO THE INITIAL GROUP OF CLUSTER"
Dcs.add_to_clusters(reference=reference_2, dataset_uri=leiden_GRAPH, property_uri=leiden_cluster_PROPS, activated=False)

print "\n2.4 ADDING [H2020] RESOURCES TO THE INITIAL GROUP OF CLUSTER"
Dcs.add_to_clusters(reference=reference_2, dataset_uri=h2020_GRAPH, property_uri=h2020_cluster_PROPS, activated=False)

print "\n2.5 ADDING [ORGREG] RESOURCES TO THE INITIAL GROUP OF CLUSTER"
Dcs.add_to_clusters(reference=reference_2, dataset_uri=orgreg_GRAPH, property_uri=orgreg_cluster_PROPS, activated=False)

print "\n2.6 ADDING [ORGREG] RESOURCES TO THE INITIAL GROUP OF CLUSTER"
Dcs.add_to_clusters(
    reference=reference_2, dataset_uri=openaire_GRAPH, property_uri=openaire_cluster_PROPS, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 3. CREATING A [LINKSET] FROM A [CLUSTER]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "\n3. CREATING A LINKSET FROM A [CLUSTER]"
# # GENERATE THE MIXED-RESOURCES LINKSET
cluster = "http://risis.eu/cluster/P1041014171_au_australia"
# Dcs.linkset_from_cluster(specs=specs, cluster_uri=cluster, user_label=None, count=1, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 4. CREATING A [LINKSET] FROM A [CLUSTER REFERENCE]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "\n4. CREATING A LINKSET FROM A [CLUSTER REFERENCE]"

Linkset.cluster_specs_2_linksets(specs=specs, activated=True)

# Dcs.linkset_from_clusters(specs=specs, activated=True)


###################################################
# ADDING
###################################################
# Dcs.print cluster_meta("http://risis.eu/cluster/FR_GBs")
# Dcs.add_to_cluster("http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/orgref_20170703",
#                    "http://risis.eu/orgref_20170703/ontology/predicate/Country", activated=False)
#
#
# Dcs.create_cluster(["FR", "GB"], "http://risis.eu/dataset/grid_20170712",
#                 ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"],
# activated=False)
# #
# Dcs.add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/eter_2014",
#                     "http://risis.eu/eter_2014/ontology/predicate/Country_Code", activated=False)

# Dcs.add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/orgref_20170703",
#                     "http://risis.eu/orgref_20170703/ontology/predicate/Country", activated=False)

# reference = ""

# Dcs.add_to_clusters(reference=reference, dataset_uri=init, property_uri=props, activated=True)

# 2. ORGREF http://risis.eu/dataset/orgref_20170703
# orgref_to_add = "http://risis.eu/dataset/orgref_20170703"
# orgref_props = ["http://risis.eu/orgref_20170703/ontology/predicate/Country"]
# Dcs.add_to_clusters(reference=reference, dataset_uri=orgref_to_add, property_uri=orgref_props, activated=True)


# # 3. ORGREG http://risis.eu/dataset/orgreg_20170718
# orgreg_to_add = "http://risis.eu/dataset/orgreg_20170718"
# orgreg_props_1 = ["http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment"]
# orgreg_props_2 = ["http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_location"]
# Dcs.add_to_clusters(reference=reference, dataset_uri=orgreg_to_add, property_uri=orgreg_props_1, activated=False)
# Dcs.add_to_clusters(reference=reference, dataset_uri=orgreg_to_add, property_uri=orgreg_props_2, activated=False)
#
# # 4. ETER http://risis.eu/dataset/eter_2014
# eter_to_add = "http://risis.eu/dataset/eter_2014"
# eter_props = ["http://risis.eu/eter_2014/ontology/predicate/Country_Code",
#               "http://risis.eu/eter_2014/ontology/predicate/Country_of_foreign_institution"]
# Dcs.add_to_clusters(reference=reference, dataset_uri=eter_to_add, property_uri=eter_props, activated=False)
#

# # 2. ORGREF http://risis.eu/dataset/orgref_20170703
# eter_boundary_ds = "http://risis.eu/dataset/eter_2014_enriched"
# eter_props = ["http://risis.eu/alignment/predicate/intersects"]
# Dcs.create_clusters(initial_dataset_uri=eter_boundary_ds, property_uri=eter_props, activated=False)

###################################################
# DATA(INPUT) NEEDED AND FORMAT
###################################################

prop2 = ["http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode",
         "http://risis.eu/eter_2014/ontology/predicate/Country_Code",
         "http://risis.eu/orgref_20170703/ontology/predicate/Country"]




# Dcs.target_datatype_properties(targets, "alignmentTarget", "myLinkset")


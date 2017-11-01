import Alignments.ConstraintClustering.DatasetsResourceClustering as Dcs
import Alignments.Settings as St

###################################################
# DATA(INPUT) NEEDED AND FORMAT
###################################################

# ## GRID
grid_graph = "http://risis.eu/dataset/grid_20170712"
grid_org_type = "http://xmlns.com/foaf/0.1/Organization"
grid_org_props = ["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2004/02/skos/core#prefLabel",
                  "http://www.w3.org/2004/02/skos/core#altLabel", "http://xmlns.com/foaf/0.1/homepage"]
grid_main_dict = {
    St.graph: grid_graph,
    St.data: [{St.entity_datatype: grid_org_type, St.properties: grid_org_props}]
}

# ## ORGREF
orgref_graph = "http://risis.eu/dataset/orgref_20170703"
orgref_org_type = "http://risis.eu/orgref_20170703/ontology/class/Organisation"
orgref_org_props = ["http://risis.eu/orgref_20170703/ontology/predicate/Name",
                    "http://risis.eu/orgref_20170703/ontology/predicate/Website"]
orgref_main_dict = {
    St.graph: orgref_graph,
    St.data: [{St.entity_datatype: orgref_org_type, St.properties: orgref_org_props}]
}

# ## ORGREG
orgreg_graph = "http://risis.eu/dataset/orgre8_20170718"
orgreg_org_type = "http://risis.eu/orgreg_20170718/resource/organization"
orgreg_org_props = ["http://risis.eu/orgreg_20170718/ontology/predicate/Name_of_entity",
                    "http://risis.eu/orgreg_20170718/ontology/predicate/English_name_of_entity",
                    "http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English",
                    "http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment",
                    "http://risis.eu/orgreg_20170718/ontology/predicate/Website_of_entity"]
orgreg_main_dict = {
    St.graph: orgreg_graph,
    St.data: [{St.entity_datatype: orgreg_org_type, St.properties: orgreg_org_props}]
}

# ## ETER
eter_graph = "http://risis.eu/dataset/eter_2014"
eter_org_type = "http://risis.eu/eter_2014/ontology/class/University"
eter_org_props = ["http://risis.eu/eter_2014/ontology/predicate/Institution_Name",
                  "<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
                  "http://risis.eu/eter_2014/ontology/predicate/Name_of_foreign_institution",
                  "http://risis.eu/eter_2014/ontology/predicate/Institutional_website"]
eter_main_dict = {
    St.graph: eter_graph,
    St.data: [{St.entity_datatype: eter_org_type, St.properties: eter_org_props}]
}

specs = [grid_main_dict, orgref_main_dict, orgreg_main_dict, eter_main_dict]

prop2 = ["http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode",
         "http://risis.eu/eter_2014/ontology/predicate/Country_Code",
         "http://risis.eu/orgref_20170703/ontology/predicate/Country"]

###################################################
# CREATING MULTIPLE CLUSTERS IN ONE STEP
###################################################

# THE INITIAL DATASET IS grid_20170712
grid_GRAPH = "http://risis.eu/dataset/grid_20170712"
grid_PROPS = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
              "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]

orgref_GRAPH = "http://risis.eu/dataset/orgref_20170703"
orgref_PROPS = ["http://risis.eu/orgref_20170703/ontology/predicate/Country"]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 1. [CREATE] A GROUP OF CLUSTERS USING THE [GRID] DATASET AND
    [COUNTRY CODE] AND [COUNTRY NAME] AS CLUSTER CONSTRAINTS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "1. INITIAL GROUP OF CLUSTERS"
response = Dcs.create_clusters(initial_dataset_uri=grid_GRAPH, property_uri=grid_PROPS, strong=True, activated=False)
# reference = response["reference"]
# print reference

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 2. [ADD] NEW RESOURCES TO THE GROUP OF CLUSTERS CREATED AT STEP ONE
    USING THE [ORGREF] DATASET AND [COUNTRY CODE] AS THE CONDITION TO
    BELONG TO AN EXISTING CLUSTER.
    IF A NON EXISTING CLUSTER EXISTS IN [ORGREF] BUT NOT IN THE EXISTING
    GROUP, A NEW CLUSTER IS GENERATED AND ADDED TO THE GROUP.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "\n2. ADDING ORGREF RESOURCE TO THE INITIAL GROUP OF CLUSTER"
reference_2 = "http://risis.eu/cluster/reference/P1041014171"
Dcs.add_to_clusters(reference=reference_2, dataset_uri=orgref_GRAPH, property_uri=orgref_PROPS, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 3. CREATING A [LINKSET] FROM A [CLUSTER]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "\n3. CREATING A LINKSET FROM A [CLUSTER]"
# # GENERATE THE MIXED-RESOURCES LINKSET
cluster = "http://risis.eu/cluster/P1041014171_au_australia"
Dcs.linkset_from_cluster(specs=specs, cluster_uri=cluster, user_label=None, count=1, activated=False)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
>>> 4. CREATING A [LINKSET] FROM A [CLUSTER REFERENCE]
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "\n4. CREATING A LINKSET FROM A [CLUSTER REFERENCE]"
Dcs.linkset_from_clusters(specs=specs, reference=reference_2, activated=False)


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

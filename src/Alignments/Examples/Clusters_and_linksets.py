import Alignments.ConstraintClustering.DatasetsResourceClustering as Dcs

prop1 = [
        # GRID
        "http://www.w3.org/2004/02/skos/core#prefLabel",
         "http://www.w3.org/2004/02/skos/core#prefLabel",
         "http://www.w3.org/2004/02/skos/core#altLabel",
         "foaf:homepage",
        # ORGREF
        "http://risis.eu/orgref_20170703/ontology/predicate/Name",
         "http://risis.eu/orgref_20170703/ontology/predicate/Website",
         # ORGREG
         "http://risis.eu/orgreg_20170718/ontology/predicate/Name_of_entity",
         "http://risis.eu/orgreg_20170718/ontology/predicate/English_name_of_entity",
         "http://risis.eu/orgreg_20170718/ontology/predicate/Entity_current_name_English",
         "http://risis.eu/orgreg_20170718/ontology/predicate/Country_of_establishment",
         "http://risis.eu/orgreg_20170718/ontology/predicate/Website_of_entity",
         # ETER
         "http://risis.eu/eter_2014/ontology/predicate/Institution_Name",
         "<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
         "http://risis.eu/eter_2014/ontology/predicate/Name_of_foreign_institution",
         "http://risis.eu/eter_2014/ontology/predicate/Institutional_website"
        ]

prop2 = ["http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode",
        "http://risis.eu/eter_2014/ontology/predicate/Country_Code",
        "http://risis.eu/orgref_20170703/ontology/predicate/Country"]
#
# Dcs.linkset_from_cluster("http://risis.eu/cluster/FR_GB", prop)

# Dcs.print cluster_meta("http://risis.eu/cluster/FR_GBs")
#
#
# Dcs.create_cluster(["FR", "GB"], "http://risis.eu/dataset/grid_20170712",
#                 ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>"], activated=False)
# #
# Dcs.add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/eter_2014",
#                     "http://risis.eu/eter_2014/ontology/predicate/Country_Code", activated=False)

# Dcs.add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/orgref_20170703",
#                     "http://risis.eu/orgref_20170703/ontology/predicate/Country", activated=False)


props = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
         "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]
init = "http://risis.eu/dataset/grid_20170712"
reference = ""

# 1. INITIAL CLUSTER: CLUSTER ORGANISATION ON THE BASIS OF THEY COUNTRY
# THE INITIAL DATASET IS grid_20170712
# response = Dcs.create_clusters(initial_dataset_uri=init, property_uri=props, activated=True)
# reference = response["reference"]
if reference == "":
        reference = "http://risis.eu/cluster/b0e36733e5c5776b1dca5da9a3a531d1"
# print reference

# Dcs.add_to_clusters(reference=reference, dataset_uri=init, property_uri=props, activated=True)

# 2. ORGREF http://risis.eu/dataset/orgref_20170703
orgref_to_add = "http://risis.eu/dataset/orgref_20170703"
orgref_props = ["http://risis.eu/orgref_20170703/ontology/predicate/Country"]
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
# # GENERATE THE MIXED-RESOURCES LINKSET
# Dcs.linkset_from_clusters(reference=reference, properties=prop1, activated=False)
#
#
# # 2. ORGREF http://risis.eu/dataset/orgref_20170703
# orgref_to_add = "http://risis.eu/dataset/orgref_20170703"
# orgref_props = ["http://risis.eu/orgref_20170703/ontology/predicate/Country"]
# Dcs.create_clusters(initial_dataset_uri=orgref_to_add, property_uri=orgref_props, activated=False)
#
#
# # 2. ORGREF http://risis.eu/dataset/orgref_20170703
# eter_boundary_ds = "http://risis.eu/dataset/eter_2014_enriched"
# eter_props = ["http://risis.eu/alignment/predicate/intersects"]
# Dcs.create_clusters(initial_dataset_uri=eter_boundary_ds, property_uri=eter_props, activated=False)
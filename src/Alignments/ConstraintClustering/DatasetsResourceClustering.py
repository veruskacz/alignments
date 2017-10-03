import Alignments.NameSpace as Ns
import Alignments.Utility as Ut
import Alignments.Query as Qry
import Alignments.Settings as St


# COUNTING THE NUMBER OF TRIPLES INSERTED
def count_triples(graph):
    query = """
    SELECT (count(DISTINCT ?obj) as ?total)
    {{
      graph <{}> {{?sub ?pred ?obj .}}
    }}""".format(graph)
    response = Qry.sparql_xml_to_matrix(query)
    if response is not None:
        result = response[St.result]
        if result is not None:
            return result[1][0]
    return "0"


# COUNTING THE NUMBER OF TRIPLES INSERTED
def count_list(graph):
    query = """
    PREFIX ll: <{0}>
    SELECT (count(DISTINCT ?obj) as ?total)
    {{
      graph <{1}> {{?sub ll:list ?obj .}}
    }}""".format(Ns.alivocab, graph)
    response = Qry.sparql_xml_to_matrix(query)
    if response is not None:
        result = response[St.result]
        if result is not None:
            return result[1][0]
    return "0"


# CHECK THE CLUSTER METADATA: DATASETS CLUSTERED AMD CONSTRAINTS
def cluster_meta(cluster_uri):

    datasets = []
    constraints = []
    matrix = None

    # CHECK WHETHER THE CLUSTER EXISTS
    query = """
    SELECT ?constraint ?dataset
    {{
        GRAPH <{}>
        {{
            ?sub prov:wasDerivedFrom  ?dataset .
            ?sub ll:clusterConstraint ?constraint .
        }}
    }} """.format(cluster_uri)
    response = Qry.sparql_xml_to_matrix(query)

    # SET THE MATRIX
    if response is not None and response[St.result] is not None:
        matrix = response[St.result]

    # EXTRACT THE INFORMATION
    if matrix is not None:
        for i in range(1, len(matrix)):
            if matrix[i][0] not in constraints:
                constraints += [matrix[i][0]]
            if matrix[i][1] not in datasets:
                datasets += [matrix[i][1]]

    # RETURN THE RESULT AS A DICTIONARY
    return {'datasets': datasets, "constraints": constraints}


# VALIDATE URIS
def validate_uri(prop_list):
    # MAKING SURE THAT THE PROPERTIES ARE IN ANGLE BRACKETS
    for i in range(0, len(prop_list)):
        if Ut.is_nt_format(prop_list[i]) is False:
            prop_list[i] = "<{}>".format(prop_list[i])


# CREATE A CLUSTER AND ADD RESOURCES FROM A SELECTED DATASET WHENEVER THE RESOURCES SATISFIES THE CLUSTER'S CONSTRAINTS
def create_cluster(cluster_constraint, dataset_uri, property_uri, count=1, activated=False):

    """
    :param cluster_constraint: a ascii string to satisfy for example country name: BENIN
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param activated: boolean value for activating the function
    :return:
    """

    constraint_v = ""
    constraint = ""
    property_list = ""

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    # LIST OF CONSTRAINT OR SINGLE VALUE
    if type(cluster_constraint) is list:
        for i in range(0, len(cluster_constraint)):
            if i == 0:
                constraint += "{}".format((cluster_constraint[i]).strip())
                constraint_v += "\"{}\"".format((cluster_constraint[i]).strip())
            else:
                constraint += " {}".format((cluster_constraint[i]).strip())
                constraint_v += " \"{}\"".format((cluster_constraint[i]).strip())

    elif type(cluster_constraint) is str:
        constraint_v = "\"{}\"".format(cluster_constraint)
        constraint = str(cluster_constraint).strip()

    # LIST OF PROPERTIES OR SINGLE VALUE PROPERTY
    if type(property_uri) is list:
        # print "WE ARE IN A LIST"
        for i in range(0, len(property_uri)):
            current = property_uri[i] if Ut.is_nt_format(property_uri[i]) is True else "<{}>".format(property_uri[i])
            if i == 0:
                property_list += "({})".format(current)
            else:
                property_list += "\n\t\t\t\t | ({})".format(current)
    else:
        property_list = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

    label = constraint.replace(" ", "_")

    query = """
    PREFIX ll: <{0}>
    INSERT
    {{
        # THE CLUSTERED GRAPH
        GRAPH <{1}{2}>
        {{
            <{1}{2}> ll:initial  <{3}> .
            <{1}{2}> ll:clusterConstraint  ?constraint .
            <{1}{2}> prov:wasDerivedFrom <{3}> .
            <{1}{2}> ll:list ?resource .
        }}
    }}
    WHERE
    {{
        VALUES ?constraint {{ {5} }}
        # THE DATASET WHOSE RESOURCES NEED TO BE CLUSTERED
        GRAPH <{3}>
        {{
            ?resource {4} ?value .
            # CONVERT THE VALUE TO LOWER CASE
            BIND(lcase(str(?value)) as ?str_value)
            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?str_value, ?regexp, '$1$2') AS ?trimmed_value)
        }}
        FILTER (?trimmed_value = lcase(?constraint))
    }}
    """.format(Ns.alivocab, Ns.cluster, label, dataset_uri, property_list, constraint_v)
    # print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    inserted = Qry.boolean_endpoint_response(query)
    print "\nCLUSTER {}: {}{}".format(count, Ns.cluster, label)
    print "\tCONSTRAINT", constraint
    print "\tINSERTED STATUS: {}".format(inserted)
    # print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.cluster, label)))
    print "\tCLUSTER SIZE: {}".format(count_list("{0}{1}".format(Ns.cluster, label)))


# ADD NEW RESOURCES TO THE ALREADY EXISTING CLUSTER
def add_to_cluster(cluster_uri, dataset_uri, property_uri, count=1, activated=False):

    """
    :param cluster_uri: the cluster graph
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param activated: boolean value for activating the function
    :return:
    """

    property_list = ""
    cluster_constraint = ""
    cluster_uri = cluster_uri.strip()
    dataset_uri = dataset_uri.strip()

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    # CHECK WHETHER THE CLUSTER EXISTS
    check_cluster_query = """
    SELECT ?constraint
    {{
        GRAPH <{}>
        {{
            ?sub ll:clusterConstraint ?constraint .
        }}
    }} """.format(cluster_uri)
    # print check_cluster_query
    response = Qry.sparql_xml_to_matrix(check_cluster_query)

    # PROCEED ONLY IF THE CUSTER GRAPH EXISTS
    if response is not None:

        result = response[St.result]
        if result is not None:
            for i in range(1, len(result)):
                if i == 1:
                    cluster_constraint = "\"{}\"".format(result[i][0])
                else:
                    cluster_constraint += " \"{}\"".format(result[i][0])

            # print cluster_constraint
            cluster_constraint = str(cluster_constraint).strip()
            # property_uri = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

            # LIST OF PROPERTIES OR SINGLE VALUE PROPERTY
            if type(property_uri) is list:
                # print "WE ARE IN A LIST"
                for i in range(0, len(property_uri)):
                    property_uri[i] = property_uri[i].strip()
                    current = property_uri[i] if Ut.is_nt_format(property_uri[i]) is True else "<{}>".format(
                        property_uri[i])
                    if i == 0:
                        property_list += "({})".format(current)
                    else:
                        property_list += "\n\t\t\t\t | ({})".format(current)
            else:
                property_uri = property_uri.strip()
                property_list = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

            query = """
    PREFIX ll: <{0}>
    INSERT
    {{
        # THE CLUSTERED GRAPH
        GRAPH <{1}>
        {{
            <{1}> ll:clusterConstraint  ?constraint .
            <{1}> prov:wasDerivedFrom <{2}> .
            <{1}> ll:list ?resource .
        }}
    }}
    WHERE
    {{
        VALUES ?constraint {{ {4} }}
        # THE DATASET WHOSE RESOURCES NEED TO BE CLUSTERED
        GRAPH <{2}>
        {{
            ?resource {3} ?value .
            # CONVERT THE VALUE TO LOWER CASE
            BIND(lcase(str(?value)) as ?str_value)
            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?str_value, ?regexp, '$1$2') AS ?trimmed_value)
        }}
        FILTER (?trimmed_value = lcase(?constraint))
    }}
    """.format(Ns.alivocab, cluster_uri, dataset_uri, property_list, cluster_constraint)
            # print query

            # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
            print "\nCLUSTER {}: {}".format(count, cluster_uri)
            print "\tCLUSTER SIZE BEFORE: {}".format(count_list(cluster_uri))
            inserted = Qry.boolean_endpoint_response(query)
            print "\tINSERTED STATUS: {}".format(inserted)
            # print alignment_construct
            print "\tCLUSTER SIZE AFTER: {}".format(count_list(cluster_uri))
    else:
        print "CLUSTER DOES NOT EXIST"


# GENERATE A LINKSET FROM A CLUSTER
def linkset_from_cluster(cluster_uri, properties):

    values = ""
    constraints = ""

    # EXTRACTING THE CLUSTER METADATA MEANING DATASETS AND CONSTRAINTS
    cluster_metadata = cluster_meta(cluster_uri)
    dataset_count = len(cluster_metadata['datasets'])
    metadata = cluster_metadata['constraints']

    # CONDITION TO CONTINUE
    print "dataset_count: {}".format(dataset_count)
    if dataset_count == 0:
        return ""

    # MAKING SURE THAT THE PROPERTIES ARE IN ANGLE BRACKETS
    for i in range(0, len(properties)):
        if Ut.is_nt_format(properties[i]) is False:
            properties[i] = "<{}>".format(properties[i])
        if i == 0:
            values = "({})".format(properties[i])
        else:
            values += "\n\t\t\t\t | ({})".format(properties[i])

    # THE SPARQL QUERY DEPENDS ON THE AMOUNT OF DATASETS IN THE CLUSTERS
    for item in metadata:
        constraints += "{} ".format(item)

    # LINKSET LABEL (ID)
    identification = hash(values + constraints)
    label = "clustered_{}".format(str(identification).replace("-", "N")) \
        if str(identification).startswith("-") else "clustered_P{}".format(str(identification))
    print label

    # SPARQL QUERY
    query = """
    PREFIX ll: <{0}>
    INSERT
    {{
        GRAPH <{3}{4}>
        {{
            ?resource_0  ll:sameAs ?resource_1 .
        }}
    }}
    WHERE
    {{
        # TAKE 2 RANDOM RESOURCES FROM THE CLUSTER
        GRAPH <{1}>
        {{
            <{1}> ll:list ?resource_0 .
            <{1}> ll:list ?resource_1 .
        }}
        # FIND SOME INFORMATION ABOUT RESOURCE_O WITHIN A RANDOM GRAPH 1
        GRAPH ?dataset_0
        {{
            ?resource_0 {2} ?obj_0 .
            # TO STRING AND TO LOWER CASE
            BIND(lcase(str(?obj_0)) as ?label_0)
            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?label_0, ?regexp, '$1$2') AS ?trimmed_label)
        }}
        # FIND THE SAME INFORMATION ABOUT RESOURCE_1 WITHIN A DIFFERENT RANDOM GRAPH 2
        GRAPH ?dataset_1
        {{
            ?resource_1 {2} ?obj_1 .
            # TO STRING AND TO LOWER CASE
            BIND(lcase(str(?obj_1)) as ?label_1)
            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?label_1, ?regexp, '$1$2') AS ?trimmed_label)
        }}

        FILTER(str(?dataset_0) > str(?dataset_1))
    }}
    """.format(Ns.alivocab, cluster_uri, values, Ns.linkset, label)
    print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    inserted = Qry.boolean_endpoint_response(query)
    print "INSERTED: {}".format(inserted)
    print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.linkset, label)))


# prop = ["http://www.w3.org/2004/02/skos/core#prefLabel",
#         "<http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name>",
#         "http://risis.eu/orgref_20170703/ontology/predicate/Name"]
#
# prop2 = ["http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode",
#         "http://risis.eu/eter_2014/ontology/predicate/Country_Code",
#         "http://risis.eu/orgref_20170703/ontology/predicate/Country"]
#
#
# linkset_from_cluster("http://risis.eu/cluster/FR_GB", prop)

# print cluster_meta("http://risis.eu/cluster/FR_GBs")
#
#
# create_cluster(["FR", "GB"], "http://risis.eu/dataset/grid_20170712",
#                 "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>", activated=False)
#
#
# add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/eter_2014",
#                     "http://risis.eu/eter_2014/ontology/predicate/Country_Code", activated=False)
#
# add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/orgref_20170703",
#                     "http://risis.eu/orgref_20170703/ontology/predicate/Country", activated=False)

# VALUES ?prop_0 {{ {2} }}
# VALUES ?prop_1 {{ {2} }}


# GENERATE MULTIPLE CLUSTERS FROM AN INITIAL DATASET
def create_clusters(dataset_uri, property_uri, activated=False):

    constraint_table = None

    # MAKING SURE THAT THE PROPERTIES ARE IN ANGLE BRACKETS
    validate_uri(property_uri)

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    variables = ""
    resources = ""
    for prop in property_uri:
        name = Ut.get_uri_local_name(prop)
        variables += " ?{}".format(name)
        resources += "\n\t\t\t?resource {} ?{} .".format(prop, name)
    # print variables

    # EXTRACT CLUSTER CONSTRAINTS
    query = """
    SELECT DISTINCT {0}
    {{
        GRAPH <{1}>
        {{ {2}
        }}
    }}""".format(variables, dataset_uri, resources)
    # print query
    constraint_table_response = Qry.sparql_xml_to_matrix(query)

    if constraint_table_response is not None:
        constraint_table = constraint_table_response[St.result]
    print "TABLE OF CONSTRAINTS"
    Qry.display_matrix(constraint_table_response, is_activated=True)

    if constraint_table is None:
        return "NO CONSTRAINT COULD BE FOUND"

    for i in range(1, 4):
        create_cluster(constraint_table[i], dataset_uri, property_uri, count=i, activated=True)


props = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
         "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]
create_clusters("http://risis.eu/dataset/grid_20170712", property_uri=props, activated=True)


def add_to_clusters(initial, dataset_uri, property_uri, activated=False):

    print "ADDING TO EXISTING CLUSTERS"

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    resources = ""
    cluster_table = None

    # SET THE PROPERTY OF THE CONSTRAINTS
    if type(property_uri) is list:
        for i in range(0, len(property_uri)):
            prop = "<{}>".format(property_uri[i]) \
                if Ut.is_nt_format(property_uri[i]) is False else "{}".format(property_uri[i])
            if i == 0:
                resources += "\n\t\t\t?resource {} ".format(prop)
            else:
                resources += "\n\t\t\t\t| {} ".format(prop)
    else:
        prop = "<{}>".format(property_uri) if Ut.is_nt_format(property_uri) is False else "{}".format(property_uri)
        resources = "?resource {} ?constraint .".format(prop, )

    # FIND THE CLUSTERS OF INTEREST BASED ON THE CONSTRAINTS
    query = """
    PREFIX ll: <{0}>
    SELECT DISTINCT ?cluster
    {{
        # EXTRACT THE CONSTRAINTS
        GRAPH <{3}>
        {{
            {4} ?constraint_1 .
        }}
        # FIND A CLUSTER FOR WITCH YOU SHARE THE SAME CONSTRAINT
        GRAPH ?cluster
        {{
            ?cluster ll:initial  <{1}> .
            ?cluster ll:clusterConstraint ?constraint_2 .
        }}
        FILTER (LCASE(?constraint_1) = LCASE(?constraint_2) )
    }}
    """.format(Ns.alivocab, initial, "PS", dataset_uri, resources)
    # print query

    # RUN THE QUERY AGAINST  THE TRIPLE STORE
    cluster_table_response = Qry.sparql_xml_to_matrix(query)
    if cluster_table_response is not None:
        cluster_table = cluster_table_response[St.result]
    print "TABLE OF COMPATIBLE CLUSTER"
    Qry.display_matrix(cluster_table_response, is_activated=True)

    # NO RESULT FOUND
    if cluster_table is None:
        print "NO COMPATIBLE CLUSTER WERE FOUND."
        return "NO COMPATIBLE CLUSTER WERE FOUND."

    # ADD TO THE COMPATIBLE CLUSTERS FOUND
    for i in range(1, len(cluster_table)):
        add_to_cluster(cluster_table[i][0], dataset_uri, property_uri, count=i, activated=True)


init = "http://risis.eu/dataset/grid_20170712"
add_to_clusters(initial=init, dataset_uri="http://risis.eu/dataset/orgref_20170703",
                property_uri=["http://risis.eu/orgref_20170703/ontology/predicate/Country",
                              "http://risis.eu/orgref_20170703/ontology/predicate/Name"], activated=True)

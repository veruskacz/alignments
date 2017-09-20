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


# CREATE A CLUSTER AND ADD RESOURCES FROM A SELECTED DATASET WHENEVER THE RESOURCES SATISFIES THE CLUSTER'S CONSTRAINTS
def create_cluster(cluster_constraint, dataset_uri, property_uri, activated=False):

    """
    :param cluster_constraint: a ascii string to satisfy for example country name: BENIN
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param activated: boolean value for activating the function
    :return:
    """

    constraint_v = ""
    constraint = ""

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

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

    label = constraint.replace(" ", "_")
    property_uri = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

    query = """
    PREFIX ll: <{0}>
    INSERT
    {{
        # THE CLUSTERED GRAPH
        GRAPH <{1}{2}>
        {{
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
    """.format(Ns.alivocab, Ns.cluster, label, dataset_uri, property_uri, constraint_v)
    print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    inserted = Qry.boolean_endpoint_response(query)
    print "{INSERTED: {}}".format(inserted)
    print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.cluster, label)))


# ADD NEW RESOURCES TO THE ALREADY EXISTING CLUSTER
def add_to_cluster(cluster_uri, dataset_uri, property_uri, activated=False):

    """
    :param cluster_uri: the cluster graph
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param activated: boolean value for activating the function
    :return:
    """

    cluster_constraint = ""
    cluster_uri = cluster_uri.strip()
    dataset_uri = dataset_uri.strip()
    property_uri = property_uri.strip()

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

            print cluster_constraint
            cluster_constraint = str(cluster_constraint).strip()
            property_uri = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

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
    """.format(Ns.alivocab, cluster_uri, dataset_uri, property_uri, cluster_constraint)
            print query

            # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
            print "TRIPLE COUNT BEFORE: {}".format(count_triples(cluster_uri))
            inserted = Qry.boolean_endpoint_response(query)
            print "{INSERTED: {}}".format(inserted)
            # print alignment_construct
            print "TRIPLE COUNT AFTER: {}".format(count_triples(cluster_uri))
    else:
        print "CLUSTER DOES NOT EXIST"


# print cluster_meta("http://risis.eu/cluster/FR_GBs")
#
#
# create_cluster(["FR", "GB"], "http://risis.eu/dataset/grid_20170712",
#                 "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>", activated=False)
#
#
# add_to_cluster(" http://risis.eu/cluster/FR_GB", "http://risis.eu/dataset/eter_2014",
#                     "http://risis.eu/eter_2014/ontology/predicate/Country_Code", activated=False)

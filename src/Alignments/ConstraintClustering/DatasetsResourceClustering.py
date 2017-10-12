import Alignments.NameSpace as Ns
import Alignments.Utility as Ut
import Alignments.Query as Qry
import Alignments.Settings as St
import cStringIO as Buffer


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
    PREFIX ll: <{0}>
    PREFIX prov: <{1}>
    SELECT ?constraint ?dataset
    {{
        GRAPH <{2}>
        {{
            ?sub prov:wasDerivedFrom  ?dataset .
            ?sub ll:clusterConstraint ?constraint .
        }}
    }} """.format(Ns.alivocab, Ns.prov, cluster_uri)
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


# GIVEN A CONSTRAINT, CREATE A CLUSTER AND ADD RESOURCES FROM A SELECTED DATASET
# WHENEVER ITS RESOURCES SATISFIES THE CLUSTER'S CONSTRAINTS PROVIDED
def create_cluster(cluster_constraint, dataset_uri, property_uri, count=1, reference=None, activated=False):

    """
    :param cluster_constraint: a ascii string to satisfy for example country name: BENIN
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI for which the constraints are evaluated against.
    :param count: just an int for counting the number of clusters
    :param reference: name associated to a group of clusters
    :param activated: boolean value for activating the function
    :return:
    """

    # CONSTRAINT["UK", ""UNITED KINGDOM]
    # DATASET = "http://risis.eu/dataset/grid_20170712"
    # property_uri = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
    # "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]
    # reference = "ORG_COUNTRY"

    print "\n>>> CREATING A NEW CLUSTER\n~~~~~~~~~~~~~~~~~~~~~~~~~~"

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
            current = str(cluster_constraint[i]).strip()
            if i == 0 and current:
                constraint += "{}".format(current)
                constraint_v += "\"{}\"".format((cluster_constraint[i]).strip())
            elif current:
                constraint += " {}".format(current)
                constraint_v += " \"{}\"".format(current)

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

    # THE GROUP NAME SHARED BY ALL CLUSTERS
    if reference is None:
        group_name = Ut.get_uri_local_name(property_list)
    else:
        group_name = reference
    # print group_name

    query = """
    PREFIX ll: <{0}>
    PREFIX prov: <{7}>
    INSERT
    {{
        # THE CLUSTERED GRAPH
        GRAPH <{1}{2}>
        {{
            <{1}{2}> ll:reference  \"{6}\" .
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
    """.format(Ns.alivocab, Ns.cluster, label, dataset_uri, property_list, constraint_v, group_name, Ns.prov)
    # print query

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    inserted = Qry.boolean_endpoint_response(query)
    print "\nCLUSTER {}: {}{}".format(count, Ns.cluster, label)
    print "\t{:15} : {}".format("GROUP NAME", group_name)
    print "\t{:15} : {}".format("DERIVED FROM", dataset_uri)
    print "\t{:15} : {}".format("CONSTRAINT", constraint)
    print "\t{:15} : {}".format("INSERTED STATUS", inserted)
    # print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.cluster, label)))
    print "\t{:15} : {}".format("CLUSTER SIZE", count_list("{0}{1}".format(Ns.cluster, label)))

    return {St.message: "THE CLUSTER WAS SUCCESSFULLY EXECUTED.", St.result: group_name}


# ADD NEW RESOURCES TO THE ALREADY EXISTING CLUSTER
def add_to_cluster(cluster_uri, dataset_uri, property_uri, count=1, activated=False):

    """
    :param cluster_uri: the cluster graph
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param count: just an int for counting the number of clusters
    :param activated: boolean value for activating the function
    :return:
    """

    print "\n>>> ADDING TO A SINGLE NEW CLUSTER\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

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
    PREFIX ll: <{}>
    SELECT ?constraint
    {{
        GRAPH <{}>
        {{
            ?sub ll:clusterConstraint ?constraint .
        }}
    }} """.format(Ns.alivocab, cluster_uri)
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
    PREFIX prov: <{5}>
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
    """.format(Ns.alivocab, cluster_uri, dataset_uri, property_list, cluster_constraint, Ns.prov)
            # print query

            # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
            print "\nCLUSTER {}: {}".format(count, cluster_uri)
            print "\t{:20} : {}".format("CLUSTER SIZE BEFORE", count_list(cluster_uri))
            inserted = Qry.boolean_endpoint_response(query)
            print "\t{:20} : {}".format("INSERTED STATUS", inserted)
            # print alignment_construct
            print "\t{:20} : {}".format("CLUSTER SIZE AFTER", count_list(cluster_uri))
    else:
        print "CLUSTER DOES NOT EXIST"


# GENERATE A LINKSET FROM A CLUSTER
def linkset_from_cluster(cluster_uri, properties, user_label=None, count=1):

    values = ""
    constraints = ""
    # print cluster_uri

    # EXTRACTING THE CLUSTER METADATA MEANING DATASETS AND CONSTRAINTS
    cluster_metadata = cluster_meta(cluster_uri)
    dataset_count = len(cluster_metadata['datasets'])
    metadata = cluster_metadata['constraints']

    # CONDITION TO CONTINUE
    if dataset_count == 0:
        message = "\nUNABLE TO CREATE A LINKSET AS THE DATASET COUNT " \
                  "(number of datasets involved in the cluster) IS {}.".format(dataset_count)
        print message
        return {St.message: message}

    # MAKING SURE THAT THE PROPERTIES URI ARE IN ANGLE BRACKETS
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
    if user_label is None:
        identification = hash(values + constraints)
        label = "clustered_{}".format(str(identification).replace("-", "N")) \
            if str(identification).startswith("-") else "clustered_P{}".format(str(identification))
        print label
    else:
        label = str(user_label).replace(" ", "_")

    # SPARQL QUERY
    query = """
    # CREATION OF A LINKSET OF MIXED-RESOURCES
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
    # print query
    print "\nRUN {}: {}".format(count, cluster_uri)
    print "\t{:20}: {}".format("LINKSET", label)
    print "\t{:20}: {}".format("LINKSET SIZE BEFORE", Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, label)))
    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    inserted = Qry.boolean_endpoint_response(query)
    print "\t{:20}: {}".format("LINKSET SIZE AFTER", Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, label)))
    print "INSERTED STATUS: {}".format(inserted)
    # print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.linkset, label)))


# GENERATE MULTIPLE CLUSTERS FROM AN INITIAL DATASET
def create_clusters(initial_dataset_uri, property_uri, reference=None, not_exists=False, activated=False):

    """ CREATE CLUSTERS TAKES AS INPUT

        1. INITIAL DATASET: the dataset for witch the resources will be clustered.

        2. PROPERTY: used as the basis on which clusters are created.
        When a list of properties [A, B, C] is provided, they are used ad A or B or C and
        used for the name of the cluster as cluster:A_B_C.

        3. REFERENCE: serves as the unifying name shared by all clusters.

    """
    print "\n>>> CREATING NEW CLUSTERS (MULTIPLE)\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return {St.message: "THE FUNCTION IS NOT ACTIVATE", "reference": ""}

    constraint_table = None
    property_list = ""

    # MAKING SURE THAT THE PROPERTIES ARE IN ANGLE BRACKETS
    validate_uri(property_uri)

    # LIST OF PROPERTIES OR SINGLE VALUE PROPERTY
    if type(property_uri) is list:
        # print "WE ARE IN A LIST"
        for i in range(0, len(property_uri)):
            current = property_uri[i] if Ut.is_nt_format(property_uri[i]) is True else "<{}>".format(property_uri[i])
            current = current.strip()
            if i == 0 and current:
                property_list += "({})".format(current)
            elif current:
                property_list += "\n\t\t\t\t | ({})".format(current)
    else:
        property_list = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

    # COMPUTE THE GROUP NAME SHARED BY ALL CLUSTERS
    if reference is None:
        group_name = Ut.get_uri_local_name(property_list)
    else:
        group_name = reference
    # print "group_name: ", group_name

    # EXTRACT CLUSTER CONSTRAINTS
    # FIND NEW CLUSTERS THAT DID NOT EXIST IN THE GROUP OF CLUSTERS
    append = "#"
    if not_exists is True:
        append = ""

    variables = ""
    resources = ""
    not_exists_t = ""
    for i in range(0, len(property_uri)):
        name = Ut.get_uri_local_name(property_uri[i])
        variables += " ?{}".format(name)
        if i == 0:
            resources += "\n\t\t\t?resource {} ?{} .".format(property_uri[i], name)
            not_exists_t += "\n\t\t\t{}?cluster ll:clusterConstraint ?{} .".format(append, name)
        else:
            resources += "\n\t\t\t?resource {} ?{} .".format(property_uri[i], name)
            not_exists_t += "\n\t\t\t{}?cluster ll:clusterConstraint ?{} .".format(append, name)
    # print variables


    query = """
    PREFIX ll: <{6}>
    SELECT DISTINCT {0}
    {{
        GRAPH <{1}>
        {{ {2}
        }}
        {4}FILTER NOT EXISTS {{
            # FIND AN EXISTING CLUSTER FOR WITCH YOU SHARE THE SAME CONSTRAINT
            {4}GRAPH ?cluster
            {4}{{
            {4}    ?cluster ll:reference  "{3}" . {5}
            {4}}}
        {4}}}
    }}""".format(variables, initial_dataset_uri, resources, reference, append, not_exists_t, Ns.alivocab,)
    print query
    constraint_table_response = Qry.sparql_xml_to_matrix(query)

    if constraint_table_response is not None:
        constraint_table = constraint_table_response[St.result]
    print "TABLE OF CONSTRAINTS"
    Qry.display_matrix(constraint_table_response, is_activated=True)

    if constraint_table is None:
        print "NO CONSTRAINT COULD BE FOUND"
        return {St.message: "NO CONSTRAINT COULD BE FOUND", "reference": group_name}

    for i in range(1, len(constraint_table)):
    # for i in range(1, 7):
        create_cluster(
            constraint_table[i], initial_dataset_uri, property_uri, count=i, reference=group_name, activated=True)


    return {St.message: "", "reference": group_name}


# ADD TO EXISTING CLUSTERS
def add_to_clusters(reference, dataset_uri, property_uri, activated=False):

    print "\n>>> ADDING TO EXISTING CLUSTERS (MULTIPLE)\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    resources = ""

    # SET THE PROPERTY OF THE CONSTRAINTS
    if type(property_uri) is list:
        for i in range(0, len(property_uri)):
            prop = "<{}>".format(property_uri[i]) \
                if Ut.is_nt_format(property_uri[i]) is False else "{}".format(property_uri[i])
            if i == 0:
                resources += "?resource {} ".format(prop)
            else:
                resources += "\n\t\t\t\t| {} ".format(prop)
    else:
        prop = "<{}>".format(property_uri) if Ut.is_nt_format(property_uri) is False else "{}".format(property_uri)
        resources = "?resource {} ?constraint .".format(prop, )

    def cluster_extraction(not_exists=False):

        append1 = ""
        append2 = ""
        cluster_matrix = None
        if not_exists is True:
            append1 = "!"
            append2 = "?constraint_1 #"

        # FIND THE CLUSTERS OF INTEREST BASED ON THE CONSTRAINTS
        query = """
    PREFIX ll: <{0}>
    SELECT DISTINCT {5}?cluster
    {{
        # EXTRACT THE CONSTRAINTS
        # SHOWS THE VALUES OF THE CONSTRAINT PROPERTY
        GRAPH <{2}>
        {{
            {3} ?constraint_1 .
        }}

        # FIND AN EXISTING CLUSTER FOR WITCH YOU SHARE THE SAME CONSTRAINT
        GRAPH ?cluster
        {{
            ?cluster ll:reference  \"{1}\" .
            ?cluster ll:clusterConstraint ?constraint_2 .
        }}
        FILTER (LCASE(?constraint_1) {4}= LCASE(?constraint_2) )
    }}
    """.format(Ns.alivocab, reference, dataset_uri, resources, append1, append2)
        print query

        # RUN THE QUERY AGAINST  THE TRIPLE STORE
        cluster_table_response = Qry.sparql_xml_to_matrix(query)
        if cluster_table_response is not None:
            cluster_matrix = cluster_table_response[St.result]
        if not_exists is True:
            print "\nTABLE OF NOT COMPATIBLE CLUSTER"
        else:
            print "TABLE OF COMPATIBLE CLUSTER"
        Qry.display_matrix(cluster_table_response, is_activated=True)
        return cluster_matrix

    print "\n-> PHASE 1: COMPATIBLE CLUSTERS"
    # EXTRACTING COMPATIBLE  CLUSTERS
    cluster_table = cluster_extraction(not_exists=False)
    # ADDING TO EXISTING CLUSTERS
    if cluster_table is None:
        print "NO COMPATIBLE CLUSTERS WERE FOUND."
    # ADD TO THE COMPATIBLE CLUSTERS FOUND
    else:
        for i in range(1, len(cluster_table)):
        # for i in range(1, 4):
            add_to_cluster(cluster_table[i][0], dataset_uri, property_uri, count=i, activated=True)

    print "\n-> PHASE 2: NO COMPATIBLE CLUSTERS => CREATION OF NEW CLUSTERS"
    # EXTRACTING  CLUSTERS FOR WITCH A MATCH WAS NOT FOUND
    # constraint_not_exists_table = cluster_extraction(not_exists=True)
    # if constraint_not_exists_table is None:
    #     print "NO COMPATIBLE CLUSTERS WERE FOUND."
    #     return "NO NEW CLUSTERS WERE CREATED."
    # else:

    create_clusters(dataset_uri, property_uri, reference=reference, not_exists=True, activated=True)


# FROM MULTIPLE CLUSTERS TO A SINGLE MULTI SOURCES LINKSET
def linkset_from_clusters(reference, properties, activated=False):

    print "\n>>> CREATING A MIXED RESOURCES-LINKSET\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    # EXTRACT ALL CLUSTERS THAT SHARE THE SAME INITIAL DATASET THERE ARE DERIVED FROM
    query = """
    # FIND A CLUSTER FOR WITCH YOU SHARE THE SAME CONSTRAINT
    PREFIX ll: <{0}>
    SELECT ?cluster
    {{
        GRAPH ?cluster
        {{
            ?cluster ll:reference  \"{1}\" .
        }}
    }}
    """.format(Ns.alivocab, reference)
    # print query

    # RUN THE QUERY AGAINST  THE TRIPLE STORE
    cluster_table_response = Qry.sparql_xml_to_matrix(query)
    cluster_table = cluster_table_response[St.result]

    print "\t>>> TABLE OF COMPATIBLE CLUSTER(S) FOUND"
    Qry.display_matrix(cluster_table_response, is_activated=True)
    # print "cluster_table:", cluster_table_response
    if cluster_table is None:
        return "NO LINKSET COULD BE GENERATED AS NOT MATCHING CLUSTER COULD BE FOUND."

    # BUILD THE STRING FOR GENERATING THE MIXED RESOURCE LINKSET
    builder = Buffer.StringIO()
    for i in range(1, len(cluster_table)):
        builder.write(" {}".format(cluster_table[i]))

    # LINKSET LABEL (ID)
    identification = hash(builder.getvalue())
    label = "clustered_{}".format(str(identification).replace("-", "N")) \
        if str(identification).startswith("-") else "clustered_P{}".format(str(identification))
    # print label

    # CREATE AND ADD RESOURCES TO THE LINKSET
    for i in range(1, len(cluster_table)):
        linkset_from_cluster(cluster_table[i][0], properties, user_label=label, count=i)

# TODO ADD THE DIFFERENCE => FILTER NOT EXISTS
# TODO MERGING CLUSTER
# TODO stardog-admin query list
# TODO stardog-admin query kill 66

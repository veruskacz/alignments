import Alignments.NameSpace as Ns
import Alignments.Utility as Ut
import Alignments.Query as Qry
import Alignments.Settings as St
import cStringIO as Buffer
import datetime


"""
# 1. DOCUMENTING A CLUSTER
cluster:US
    a                       ll:Cluster ;
    ll:hasReference         <reference url> ;
    ll:hasConstraint        constraint_1 ; constraint_2 ;
    ll:list                 <url1>, <url2>, ... .

# 2. ASSIGNING A NAME TO THE CLUSTER
<reference url>
    a               ll:ClusterReference ;
    rdfs:label              "country" .

# 3. DOCUMENTING THE CLUSTER'S CONSTRAINT METADATA
constraint_1
    a               ll:Constraint ;
    ll:hasValue     "US" ;
    ll:target       dataset:grid .
    ll:hasProperty  property:countryCode .

constraint_2
    a               ll:Constraint ;
    ll:hasValue     "UNITES STATE" ;
    ll:target       dataset:grid ;
    ll:hasProperty  property:countryName .
"""

_format = "%a, %d %b %Y %H:%M:%S "
print "\n{:>80}\n".format(datetime.datetime.today().strftime(_format))


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
    SELECT ?cluster_ref ?dataset ?label
    {{
        GRAPH <{2}>
        {{
            # 1. THE REFERENCE
            ?cluster  ll:hasReference  ?cluster_ref .

            # 2. THE REFERENCE LABEL
            ?cluster_ref  rdfs:label  ?label .

            # 3. THE CONSTRAINT
            ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .

            ?URL_CONSTRAINT  void:target  ?dataset .
        }}
    }} """.format(Ns.alivocab, Ns.prov, cluster_uri)
    # print query
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


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    CREATING A SINGLE CLUSTER OR MULTIPLE CLUSTERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# GIVEN A CONSTRAINT, CREATE A CLUSTER AND ADD RESOURCES FROM A SELECTED DATASET
# WHENEVER ITS RESOURCES SATISFIES THE CLUSTER'S CONSTRAINTS PROVIDED
def create_cluster(cluster_constraint, dataset_uri, property_uri, count=1,
                   reference=None, group_name=None, activated=False):

    """
    :param cluster_constraint: a ascii string to satisfy for example country name: BENIN
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI for which the constraints are evaluated against.
    :param count: just an int for counting the number of clusters
    :param reference: name associated to a group of clusters
    :param activated: boolean value for activating the function
    :param group_name: the label for the reference
    :return:
    """

    # CONSTRAINT["UK", ""UNITED KINGDOM]
    # DATASET = "http://risis.eu/dataset/grid_20170712"
    # property_uri = ["<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>",
    # "<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>"]
    # reference = "ORG_COUNTRY"

    print "\n>>> CREATING A NEW CLUSTER\n~~~~~~~~~~~~~~~~~~~~~~~~~~"
    # print "reference:", reference

    constraint_v = ""
    constraint = ""
    property_list = ""
    properties = ""
    property_bind = ""
    fetch = ""
    plans = []

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    # LIST OF CONSTRAINT OR SINGLE VALUE
    if type(cluster_constraint) is list:
        for i in range(0, len(cluster_constraint)):
            current = str(cluster_constraint[i]).strip().lower()
            if i == 0 and current:
                constraint += "{}".format(current)
                constraint_v += "\"{}\"".format(current)
            elif current:
                constraint += " {}".format(current)
                constraint_v += " \"{}\"".format(current)

    elif type(cluster_constraint) is str:
        constraint_v = "\"{}\"".format(cluster_constraint)
        constraint = str(cluster_constraint).strip()

    # LIST OF PROPERTIES OR SINGLE VALUE PROPERTY
    if type(property_uri) is list:

        plans = property_builder(property_uri)

        # print "WE ARE IN A LIST"
        for i in range(0, len(property_uri)):
            current = property_uri[i] if Ut.is_nt_format(property_uri[i]) is True else "<{}>".format(property_uri[i])
            if i == 0:
                property_list += "({})".format(current)
                properties += "?prop_{}".format(i)
                property_bind += "BIND( IRI(\"{}\") AS ?prop_{} )".format(current, i)
                fetch += """
            {{ BIND( IRI("{0}") as ?prop_path )
            ?URL_CONSTRAINT  ll:hasProperty  ?prop_path . }}""".format(current)

            else:
                property_list += "\n\t\t\t\t | ({})".format(current)
                properties += ", ?prop_{}".format(i)
                property_bind += "\n\t\tBIND( IRI(\"{}\") AS ?prop_{} )".format(current, i)
                fetch += """
            UNION {{ BIND( IRI("{0}") as ?prop_path )
            ?URL_CONSTRAINT  ll:hasProperty  ?prop_path . }}""".format(current)

    else:
        property_list = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

    label = constraint.replace(" ", "_")

    # THE GROUP NAME SHARED BY ALL CLUSTERS
    if group_name is None:
        group_name = Ut.get_uri_local_name(property_list)
    # print group_name

    # EXAMPLE
    # """
    #     PREFIX ll: <http://risis.eu/alignment/predicate/>
    # PREFIX prov: <http://www.w3.org/ns/prov#>
    # INSERT
    # {
    #     # THE CLUSTERED GRAPH
    #     GRAPH <http://risis.eu/cluster/AU_Australia>
    #     {
    #         # 1. THE REFERENCE
    #         <http://risis.eu/cluster/AU_Australia> ll:hasReference  ?cluster_ref .
    #
    #         # 2. THE REFERENCE LABEL
    #         ?cluster_ref rdfs:label "hasAddress_countryCode_hasAddress_countryName" .
    #
    #         # 3. THE CONSTRAINT
    #         <http://risis.eu/cluster/AU_Australia>  ll:hasConstraint  ?URL_CONSTRAINT .
    #
    #         # 4. CONSTRAINT'S METADATA
    #         ?URL_CONSTRAINT  ll:hasValue  ?constraint .
    #         ?URL_CONSTRAINT  void:target  <http://risis.eu/dataset/grid_20170712> .
    #         ?URL_CONSTRAINT  ll:hasProperty  ?prop_0, ?prop_1 .
    #
    #         # 5. THE LIST OR RESOURCES
    #         <http://risis.eu/cluster/AU_Australia> ll:list ?resource .
    #     }
    # }
    # WHERE
    # {
    #     # CONSTRAINT VALUES
    #     VALUES ?constraint { "AU" "Australia" }
    #
    #     # BIND CLUSTER CONSTRAINT URL
    #     BIND( MD5(lcase(str("""http://risis.eu/dataset/grid_20170712
    #       (<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>)
    # 	    | (<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>)"""))) AS ?hashed )
    #     BIND( CONCAT("http://risis.eu/cluster_constrain/cluster/",?hashed) as ?pre )
    #     BIND(iri(?pre) as ?URL_CONSTRAINT)
    #
    #     # BIND CLUSTER NAME URL
    #     BIND( replace("http://risis.eu/cluster/#","#", MD5(STR(NOW()))) as ?name )
    #     BIND(iri(?name) as ?cluster_ref)
    #
    #     # BIND PROPERTIES TO OVERCOME PROPERTY PATH
    #     BIND( IRI("<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>") AS ?prop_0 )
    #     BIND( IRI("<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>") AS ?prop_1 )
    #
    #     # THE DATASET WHOSE RESOURCES NEED TO BE CLUSTERED
    #     GRAPH <http://risis.eu/dataset/grid_20170712>
    #     {
    #         ?resource (<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryCode>)
    # 		 | (<http://www.grid.ac/ontology/hasAddress>/<http://www.grid.ac/ontology/countryName>) ?value .
    #
    #         # CONVERT THE VALUE TO LOWER CASE
    #         BIND(lcase(str(?value)) as ?str_value)
    #
    #         # VALUE TRIMMING
    #         BIND('^\\s+(.*?)\\s*$|^(.*?)\\s+$' AS ?regexp)
    #         BIND(REPLACE(?str_value, ?regexp, '$1$2') AS ?trimmed_value)
    #     }
    #     FILTER (?trimmed_value = lcase(?constraint))
    #
    #     # DO NOT CREATE THE SAME THING AGAIN OTHERWISE
    #     # THE SAME CLUSTER WILL HAVE MULTIPLE REFERENCES
    #     FILTER NOT EXISTS
    #     {
    #
    #         GRAPH <http://risis.eu/cluster/AU_Australia>
    #         {
    #             # 3. THE CONSTRAINT
    #             <http://risis.eu/cluster/AU_Australia>  ll:hasConstraint  ?URL_CONSTRAINT .
    #
    #             # 4. CONSTRAINT'S METADATA
    #             ?URL_CONSTRAINT  ll:hasValue  ?constraint .
    #             ?URL_CONSTRAINT  void:target  <http://risis.eu/dataset/grid_20170712> .
    #             # ?URL_CONSTRAINT  ll:hasProperty
    #         }
    #     }
    # }
    # """

    if reference is None:
        comment_ref = ""
        comment_ref_2 = "#"
    else:
        comment_ref = "#"
        comment_ref_2 = ""

    date = Ut.hash_it("{}".format(datetime.datetime.today().strftime(_format)))
    query = """
    PREFIX ll: <{0}>
    PREFIX prov: <{7}>
    PREFIX void: <{15}>
    INSERT
    {{
        # THE CLUSTERED GRAPH
        GRAPH ?insertGraphURI
        {{
            # 1. THE REFERENCE
            {12}?insertGraphURI  ll:hasReference  ?cluster_ref .
            {13}?insertGraphURI  ll:hasReference  <{14}> .

            # 2. THE REFERENCE LABEL
            {12}?cluster_ref  rdfs:label  \"{6}\" .
            {13}?cluster_ref  rdfs:label  \"{6}\" .

            # 3. THE CONSTRAINT
            ?insertGraphURI  ll:hasConstraint  ?URL_CONSTRAINT .

            # 4. CONSTRAINT'S METADATA
            ?URL_CONSTRAINT  ll:hasValue  ?constraint .
            ?URL_CONSTRAINT  void:target  <{3}> .
            ?URL_CONSTRAINT  ll:hasProperty  {10} .

            # 5. THE LIST OR RESOURCES
            ?insertGraphURI  ll:list  ?resource .
        }}
    }}
    WHERE
    {{
        # NAME
        BIND( "{20}" AS ?code)
        BIND( CONCAT("{1}", ?code, "_", "{2}") AS ?insertGraph )
        BIND(iri(?insertGraph) as ?insertGraphURI)

        # CONSTRAINT VALUES
        VALUES ?constraint {{ {5} }}

        # BIND CLUSTER NAME URL
        BIND( replace(\"{9}reference/#\",\"#\", ?code) as ?name )
        BIND(iri(?name) as ?cluster_ref)

        # BIND CLUSTER CONSTRAINT URL
        BIND(MD5(str(?constraint)) AS ?hashed )
        BIND( CONCAT("{8}cluster/constraint/",?hashed) as ?pre )
        BIND(iri(?pre) as ?URL_CONSTRAINT)

        # BIND PROPERTIES TO OVERCOME PROPERTY PATH
        {11}

        # THE DATASET WHOSE RESOURCES NEED TO BE CLUSTERED
        GRAPH <{3}>
        {{
            ### 1. THE RESOURCE AND ITS VALUE
            ?resource {4} ?value .

            ### 2. CONVERT THE VALUE TO LOWER CASE
            BIND(lcase(str(?value)) as ?str_value)

            ### 3. VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?str_value, ?regexp, '$1$2') AS ?trimmed_value)

            ### 4. EXTRACT THE PROPERTY OR PROPERTY PATH FOR DOCUMENTATION {16}

            ### 5. BIND THE PROPERTY OR PROPERTY PATH FOR CONFIRMATION {17}
        }}

        ### FILTER BASED ON THE CONSTRAINT
        FILTER (?trimmed_value = lcase(?constraint))

        ### FILTER THE RIGHT PROPERTY {18}

        # DO NOT CREATE THE SAME THING AGAIN OTHERWISE
        # THE SAME CLUSTER WILL HAVE MULTIPLE REFERENCES
        FILTER NOT EXISTS
        {{
            GRAPH ?cluster
            {{
                # 3. THE CONSTRAINT
                ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .

                # 4. CONSTRAINT'S METADATA
                ?URL_CONSTRAINT  ll:hasValue  ?constraint .
                ?URL_CONSTRAINT  void:target  <{3}> .
                #?URL_CONSTRAINT  ll:hasProperty  {19} .
            }}
        }}
    }}
    """.format(
        # 0          1           2      3            4              5             6           7
        Ns.alivocab, Ns.cluster, label, dataset_uri, property_list, constraint_v, group_name, Ns.prov,
        # 8                    9           10          11              12          13             14         15
        Ns.cluster_constraint, Ns.cluster, plans[3], property_bind, comment_ref, comment_ref_2, reference, Ns.void,
        # 16      17        18        19     20
        plans[0], plans[1], plans[2], fetch, date
    )
    # print query
    # return {St.message: "THE CLUSTER WAS SUCCESSFULLY EXECUTED.",
    #         St.result: "", 'group_name': group_name}

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    # inserted = Qry.boolean_endpoint_response(query)
    Qry.boolean_endpoint_response(query)

    # FETCH THE CLUSTER REFERENCE URL
    reference_query = """
    PREFIX ll: <{0}>
    PREFIX prov: <{1}>
    SELECT DISTINCT ?cluster_ref ?cluster
    {{
        # THE CLUSTERED GRAPH
        GRAPH <{4}{5}_{6}>
        {{
            # 1. THE REFERENCE
            <{4}{5}_{6}>  ll:hasReference  ?cluster_ref .

            # 3. THE CONSTRAINT
            <{4}{5}_{6}>  ll:hasConstraint  ?URL_CONSTRAINT .

            # 4. CONSTRAINT'S METADATA
            ?URL_CONSTRAINT  ll:hasValue  ?constraint .
            ?URL_CONSTRAINT  void:target  <{2}> .
            {3}
        }}
    }}
    """.format(Ns.alivocab, Ns.prov, dataset_uri, fetch, Ns.cluster, date, label)
    # print "reference_query:", reference_query
    reference_response = Qry.sparql_xml_to_matrix(reference_query)
    # print "reference_response:", reference_response
    reference_result = reference_response[St.result]
    # print "reference_result:", reference_result

    if reference_result:
        print "\n\tCLUSTER {}: {}".format(count, "{}{}_{}".format(Ns.cluster, date, label))
        print "\t\t{:17} : {}".format("CONSTRAINT", constraint)
        print "\t\t{:17} : {}".format("GROUP NAME", group_name)
        print "\t\t{:17} : {}".format("REFERENCE", reference_result[1][0])
        print "\t\t{:17} : {}".format("Nbr OF REFERENCES", len(reference_result) - 1)
        print "\t\t{:17} : {}".format("CLUSTER SIZE", count_list("{}{}_{}".format(Ns.cluster, date, label)))

    else:
        print "\n\tCLUSTER {}: {}".format(count, None)
        print "\t\t{:17} : {}".format("CONSTRAINT", constraint)
        print "\t\t{:17} : {}".format("GROUP NAME", group_name)
        print "\t\t{:17} : {}".format("REFERENCE", None)
        print "\t\t{:17} : {}".format("CLUSTER SIZE", None)

    print "\t\t{:17} : {}".format("DERIVED FROM", dataset_uri)

    # print "\t\t{:17} : {}".format("INSERTED STATUS", inserted)
    # print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.cluster, label)))

    return {St.message: "THE CLUSTER WAS SUCCESSFULLY EXECUTED.",
            St.result: reference_result, 'group_name': group_name}


# GENERATE MULTIPLE CLUSTERS FROM AN INITIAL DATASET
def create_clusters(initial_dataset_uri, property_uri,
                    reference=None, group_name=None, not_exists=False, activated=False):

    """ CREATE CLUSTERS TAKES AS INPUT

        1. INITIAL DATASET: the dataset for witch the resources will be clustered.

        2. PROPERTY: used as the basis on which clusters are created.
        When a list of properties [A, B, C] is provided, they are used ad A or B or C and
        used for the name of the cluster as cluster:A_B_C.

        3. REFERENCE: serves as the unifying name shared by all clusters.

    """

    print "\n>>> CREATING NEW CLUSTERS (MULTIPLE)\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # ORDER THE PROPERTY
    property_uri.sort()

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
    if group_name is None:
        # print "group name in None: {}".format(property_list)
        group_name = Ut.get_uri_local_name(property_list)

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
            resources += "\n\t\t\t?resource {} ?prop_{} .".format(property_uri[i], i)
            resources += "\n\t\t\tBIND(lcase(str(?prop_{0})) as ?prop_{0}{0}) .".format(i)
            resources += "\n\t\t\tBIND(REPLACE(?prop_{0}{0}, ?regexp, '$1$2') AS ?{1}) .".format(i, name)
            not_exists_t += "\n\t\t\t\t{}?URL_CONSTRAINT ll:hasValue ?{} .".format(append, name)
        else:
            resources += "\n\n\t\t\t?resource {} ?prop_{} .".format(property_uri[i], i)
            resources += "\n\t\t\tBIND(lcase(str(?prop_{0})) as ?prop_{0}{0}) .".format(i)
            resources += "\n\t\t\tBIND(REPLACE(?prop_{0}{0}, ?regexp, '$1$2') AS ?{1}) .".format(i, name)
            not_exists_t += "\n\t\t\t\t{}?URL_CONSTRAINT ll:hasValue ?{} .".format(append, name)
    # print variables

    query = """
    PREFIX ll: <{6}>
    SELECT DISTINCT {0}
    {{
        GRAPH <{1}>
        {{
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp){2}
        }}
        {4}FILTER NOT EXISTS
        {4}{{
            # FIND AN EXISTING CLUSTER FOR WITCH YOU SHARE THE SAME CONSTRAINT
            {4}GRAPH ?cluster
            {4}{{
            {4}    ?cluster ll:hasReference  <{3}> .
            {4}    ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .{5}
            {4}}}
        {4}}}
        {4}FILTER EXISTS
        {4}{{
            ### CHECK FOR THE EXISTENCE OF THE CLUSTER. IF IT DOES NOT EXIST, TERMINATE THE PROCESS
            {4}GRAPH ?cluster
            {4}{{
            {4}    ?cluster ll:hasReference  <{3}> .
            {4}}}
        {4}}}
    }}""".format(variables, initial_dataset_uri, resources, reference, append, not_exists_t, Ns.alivocab,)
    # print query
    constraint_table_response = Qry.sparql_xml_to_matrix(query)

    if constraint_table_response is not None:
        constraint_table = constraint_table_response[St.result]

    print "TABLE OF CONSTRAINTS"
    Qry.display_matrix(constraint_table_response, is_activated=True, limit=10)

    if constraint_table is None:
        print "NO CONSTRAINT COULD BE FOUND"
        return {St.message: "NO CONSTRAINT COULD BE FOUND", "reference": reference}

    reference_uri = ""
    for i in range(1, len(constraint_table)):

        print "Count runs: ", i

        if i == 1:
            reference_uri_response = create_cluster(
                constraint_table[i], initial_dataset_uri, property_uri,
                count=i, reference=reference, group_name=group_name, activated=True)
            # print "reference_uri_response:", reference_uri_response

            if reference_uri_response[St.result]:
                reference_uri = reference_uri_response[St.result]

        else:
            if reference_uri:
                create_cluster(
                    constraint_table[i], initial_dataset_uri, property_uri,
                    count=i, reference=reference_uri[1][0], group_name=group_name, activated=True)

        if i == 3:
            break

    # print "reference_uri:",

    if reference_uri:
        return {St.message: "", "reference": reference_uri[1][0], "group_name": group_name}

    return {St.message: "", "reference": None, "group_name": group_name}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    ADDING TO A SINGLE CLUSTER OR TO MULTIPLE CLUSTERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# ADD NEW RESOURCES TO THE ALREADY EXISTING CLUSTER
def add_to_cluster_0(cluster_uri, dataset_uri, property_uri, count=1, activated=False):

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
            # 3. THE CONSTRAINT
            ?sub  ll:hasConstraint  ?URL_CONSTRAINT .

            # 4. CONSTRAINT'S METADATA
            ?URL_CONSTRAINT  ll:hasValue  ?constraint .
        }}
    }} """.format(Ns.alivocab, cluster_uri)
    # print check_cluster_query
    response = Qry.sparql_xml_to_matrix(check_cluster_query)

    # PROCEED ONLY IF THE CUSTER GRAPH EXISTS
    if response is not None:
        result = response[St.result]
        if result is not None:
            for i in range(1, len(result)):
                current = str(result[i][0]).strip().lower()
                if i == 1:
                    cluster_constraint = "\"{}\"".format(current)
                else:
                    cluster_constraint += " \"{}\"".format(current)

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


def add_to_cluster(cluster_uri, dataset_uri, property_uri, count=1, activated=False):

    """
    :param cluster_uri: the cluster graph
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param count: just an int for counting the number of clusters
    :param activated: boolean value for activating the function
    :return:
    """

    print "\n>>> ADDING TO A SINGLE NEW CLUSTER: {}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~".format(cluster_uri)

    property_list = ""
    cluster_constraint = ""
    properties = ""
    property_bind = ""
    cluster_uri = cluster_uri.strip()
    dataset_uri = dataset_uri.strip()

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return "THE FUNCTION IS NOT ACTIVATE"

    # CHECK WHETHER THE CLUSTER EXISTS AND EXTRACT THE CLUSTER CONSTRAINT
    # LABEL REQUIRED FOR A RESOURCE TO BE AN INDIVIDUAL OF THIS CLUSTER
    check_cluster_query = """
    PREFIX ll: <{}>
    SELECT ?constraint
    {{
        GRAPH <{}>
        {{
            # 3. THE CONSTRAINT
            ?sub  ll:hasConstraint  ?URL_CONSTRAINT .

            # 4. CONSTRAINT'S METADATA
            ?URL_CONSTRAINT  ll:hasValue  ?constraint .
        }}
    }} """.format(Ns.alivocab, cluster_uri)
    # print check_cluster_query
    response = Qry.sparql_xml_to_matrix(check_cluster_query)
    # print "RESPONSE:", response

    # PROCEED ONLY IF THE CLUSTER GRAPH EXISTS
    distinct_constraint = []
    if response is not None:
        result = response[St.result]
        if result is not None:

            # EXTRACT THE VALUES THAT A RESOURCES NEEDS TO VALIDATE TO BE PART OF THE CLUSTER
            for i in range(1, len(result)):
                item = result[i][0]
                if i == 1:
                    if item not in distinct_constraint:
                        cluster_constraint = "\"{}\"".format(item)
                        distinct_constraint += [item]
                else:
                    if item not in distinct_constraint:
                        cluster_constraint += " \"{}\"".format(item)
                        distinct_constraint += [item]

            print "\t>>> USING CLUSTER CONSTRAINT:", cluster_constraint
            cluster_constraint = str(cluster_constraint).strip()
            # property_uri = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(property_uri)

            # EXTRACT THE LIST OF PROPERTIES OR SINGLE VALUE PROPERTY
            if type(property_uri) is list:
                # print "WE ARE IN A LIST"
                for i in range(0, len(property_uri)):
                    property_uri[i] = property_uri[i].strip()
                    current = property_uri[i] if Ut.is_nt_format(property_uri[i]) is True else "<{}>".format(
                        property_uri[i])
                    if i == 0:
                        property_list += "({})".format(current)
                        properties += "?prop_{}".format(i)
                        property_bind += "BIND( IRI(\"{}\") AS ?prop_{} )".format(current, i)
                    else:
                        property_list += "\n\t\t\t\t | ({})".format(current)
                        properties += ", ?prop_{}".format(i)
                        property_bind += "\n\t\tBIND( IRI(\"{}\") AS ?prop_{} )".format(current, i)
            else:
                property_uri = property_uri.strip()
                property_list = property_uri if Ut.is_nt_format(property_uri) is True else "<{}>".format(
                    property_uri)

            print "\t>>> USING CLUSTER PROPERTIES:", property_list

            query = """
            PREFIX ll: <{0}>
            PREFIX prov: <{5}>
            PREFIX void: <{10}>
            INSERT
            {{
                # THE CLUSTERED GRAPH
                GRAPH <{1}>
                {{
                    # 3. THE CONSTRAINT
                    <{1}>  ll:hasConstraint  ?URL_CONSTRAINT .

                    # 4. CONSTRAINT'S METADATA
                    ?URL_CONSTRAINT  ll:hasValue  ?constraint .
                    ?URL_CONSTRAINT  void:target  <{2}> .
                    ?URL_CONSTRAINT  ll:hasProperty  {8} .

                    # 5. THE LIST OR RESOURCES
                    <{1}>  ll:list  ?resource .
                }}
            }}
            WHERE
            {{
                # CONSTRAINT VALUES
                VALUES ?constraint {{ {4} }}

                # BIND CLUSTER CONSTRAINT URL
                BIND( MD5(lcase(str(""\"{2}{3}""\"))) AS ?hashed )
                BIND( CONCAT("{6}cluster/",?hashed) as ?pre )
                BIND(iri(?pre) as ?URL_CONSTRAINT)

                # BIND PROPERTIES TO OVERCOME PROPERTY PATH
                {9}

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
            """.format(
                # 0          1            2            3              4                   5
                Ns.alivocab, cluster_uri, dataset_uri, property_list, cluster_constraint, Ns.prov,
                # 6                    7           8           9              10
                Ns.cluster_constraint, Ns.cluster, properties, property_bind, Ns.void)
            # print query

            # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
            print "\n\tCLUSTER {}: {}".format(count, cluster_uri)
            print "\t\t{:20} : {}".format("DATASET", dataset_uri)
            print "\t\t{:20} : {}".format("CLUSTER SIZE BEFORE", count_list(cluster_uri))
            inserted = Qry.boolean_endpoint_response(query)
            "\t\t{:20} : {}".format("INSERTED STATUS", inserted)
            # print alignment_construct
            print "\t\t{:20} : {}".format("CLUSTER SIZE AFTER", count_list(cluster_uri))
    else:
        print "CLUSTER DOES NOT EXIST"


# ADD TO EXISTING CLUSTERS
def add_to_clusters(reference, dataset_uri, property_uri, activated=False):



    print "\n>>> ADDING TO EXISTING CLUSTERS (MULTIPLE)\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    if reference is None:
        print "AS THE REFERENCE IS NOT PROVIDED, THE PROCESS WAS TERMINATED."
        return {St.message: "THE FUNCTION IS NOT ACTIVATE", "reference": None}

    # FUNCTION ACTIVATION
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATE"
        return {St.message: "THE FUNCTION IS NOT ACTIVATE", "reference": None}

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
            ?cluster ll:hasReference  <{1}> .

            # 3. THE CONSTRAINT
            ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .

            # 4. CONSTRAINT'S METADATA
            ?URL_CONSTRAINT  ll:hasValue  ?constraint_2  .
        }}
        FILTER (LCASE(?constraint_1) {4}= LCASE(?constraint_2) )
    }}
    """.format(Ns.alivocab, reference, dataset_uri, resources, append1, append2)
        # print query

        # RUN THE QUERY AGAINST  THE TRIPLE STORE
        cluster_table_response = Qry.sparql_xml_to_matrix(query)
        if cluster_table_response is not None:
            cluster_matrix = cluster_table_response[St.result]
        if not_exists is True:
            print "\nTABLE OF NOT COMPATIBLE CLUSTER"
        else:
            print "\t>>> TABLE OF COMPATIBLE CLUSTER"
        Qry.display_matrix(cluster_table_response, is_activated=True)
        return cluster_matrix

    # ----------------------------------------------------------------
    # >>> PHASE 1: ADDING TO COMPATIBLE/EXISTING CLUSTERS
    # not_exists=False => ONLY EXISTING CLUSTERS
    # ----------------------------------------------------------------
    print "\n-> PHASE 1: ADDING TO COMPATIBLE/EXISTING CLUSTERS"

    # EXTRACTING COMPATIBLE  CLUSTERS
    cluster_table = cluster_extraction(not_exists=False)
    # print "cluster_table:", cluster_table

    # ADDING TO EXISTING CLUSTERS
    if cluster_table is None:
        print "\t>>> NO COMPATIBLE CLUSTERS WERE FOUND."

    # ADD TO THE COMPATIBLE CLUSTERS FOUND
    else:
        for i in range(1, len(cluster_table)):
            # print "cluster_table[i][0]:", cluster_table[0]
            add_to_cluster(cluster_table[i][0], dataset_uri, property_uri, count=i, activated=True)
            if i == 3:
                break

    # ----------------------------------------------------------------
    # >>> PHASE 2: CREATION OF NEW CLUSTERS
    # not_exists=True  => ONLY CLUSTER THAT ARE NOT IN THE REFERENCE
    # ----------------------------------------------------------------
    print "\n-> PHASE 2: CREATION OF NEW CLUSTERS"
    # EXTRACTING  CLUSTERS FOR WITCH A MATCH WAS NOT FOUND
    # constraint_not_exists_table = cluster_extraction(not_exists=True)
    # if constraint_not_exists_table is None:
    #     print "NO COMPATIBLE CLUSTERS WERE FOUND."
    #     return "NO NEW CLUSTERS WERE CREATED."
    # else:

    create_clusters(dataset_uri, property_uri, reference=reference, not_exists=True, activated=True)

    return {St.message: "Added", "reference": reference}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    CREATING A LINKSET OUT OF A CLUSTERS OR OUT OF
            CLUSTERS THAT SAME REFERENCE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def helper(specs, is_source=True):

    def property_list(properties):
        values = ""
        # MAKING SURE THAT THE PROPERTIES URI ARE IN ANGLE BRACKETS
        for i in range(0, len(properties)):
            if Ut.is_nt_format(properties[i]) is False:
                properties[i] = "<{}>".format(properties[i])
            if i == 0:
                values = "({})".format(properties[i])
            else:
                values += "\n\t\t\t\t\t | ({})".format(properties[i])
        return values

    if is_source is True:
        number = 1
    else:
        number = 2
    builder = Buffer.StringIO()
    is_empty = True

    for dataset in specs:
        graph = dataset[St.graph]
        data = dataset[St.data]
        for detail in data:
            properties = detail[St.properties]
            union = "\n\t\t\t\tUNION " if is_empty is False else ""
            sub = """{3}{{
                    BIND(<{2}> AS ?dataset_{0})
                    ?resource_{0} {1} ?obj_{0} .
                    # TO STRING AND TO LOWER CASE
                    BIND(lcase(str(?obj_{0})) as ?label_{0})
                    # VALUE TRIMMING
                    BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
                    BIND(REPLACE(?label_{0}, ?regexp, '$1$2') AS ?trimmed_label)
                }} """.format(number, property_list(properties), graph, union)
            is_empty = False

            builder.write(sub)

    query = """# FIND SOME INFORMATION ABOUT RESOURCE_O WITHIN A RANDOM GRAPH {0}
            GRAPH ?dataset_{0}
            {{
                {1}
            }}
    """.format(number, builder.getvalue())
    # print query
    return query


# GENERATE A LINKSET FROM A CLUSTER
def linkset_from_cluster(specs, cluster_uri, user_label=None, count=1):

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

    # # MAKING SURE THAT THE PROPERTIES URI ARE IN ANGLE BRACKETS
    # for i in range(0, len(properties)):
    #     if Ut.is_nt_format(properties[i]) is False:
    #         properties[i] = "<{}>".format(properties[i])
    #     if i == 0:
    #         values = "({})".format(properties[i])
    #     else:
    #         values += "\n\t\t\t\t | ({})".format(properties[i])

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

    # return "DONE!1!"

    # SPARQL QUERY
    # query = """
    # # CREATION OF A LINKSET OF MIXED-RESOURCES
    # PREFIX ll: <{0}>
    # INSERT
    # {{
    #     GRAPH <{3}{4}>
    #     {{
    #         ?resource_0  ll:sameAs ?resource_1 .
    #     }}
    # }}
    # WHERE
    # {{
    #     # TAKE 2 RANDOM RESOURCES FROM THE CLUSTER
    #     GRAPH <{1}>
    #     {{
    #         <{1}> ll:list ?resource_0 .
    #         <{1}> ll:list ?resource_1 .
    #     }}
    #     # FIND SOME INFORMATION ABOUT RESOURCE_O WITHIN A RANDOM GRAPH 1
    #     GRAPH ?dataset_0
    #     {{
    #         ?resource_0 {2} ?obj_0 .
    #         # TO STRING AND TO LOWER CASE
    #         BIND(lcase(str(?obj_0)) as ?label_0)
    #         # VALUE TRIMMING
    #         BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
    #         BIND(REPLACE(?label_0, ?regexp, '$1$2') AS ?trimmed_label)
    #     }}
    #     # FIND THE SAME INFORMATION ABOUT RESOURCE_1 WITHIN A DIFFERENT RANDOM GRAPH 2
    #     GRAPH ?dataset_1
    #     {{
    #         ?resource_1 {2} ?obj_1 .
    #         # TO STRING AND TO LOWER CASE
    #         BIND(lcase(str(?obj_1)) as ?label_1)
    #         # VALUE TRIMMING
    #         BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
    #         BIND(REPLACE(?label_1, ?regexp, '$1$2') AS ?trimmed_label)
    #     }}
    #
    #     FILTER(str(?dataset_0) > str(?dataset_1))
    # }}
    # """.format(Ns.alivocab, cluster_uri, values, Ns.linkset, label)

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
            {2}
            # FIND THE SAME INFORMATION ABOUT RESOURCE_1 WITHIN A DIFFERENT RANDOM GRAPH 2
            {5}
            FILTER(str(?dataset_0) > str(?dataset_1))
        }}
        """.format(Ns.alivocab, cluster_uri, helper(specs, is_source=True),
                   Ns.linkset, label, helper(specs, is_source=False))

    print query

    # print "\nRUN {}: {}".format(count, cluster_uri)
    # print "\t{:20}: {}".format("LINKSET", label)
    # print "\t{:20}: {}".format("LINKSET SIZE BEFORE", Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, label)))
    # # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    # inserted = Qry.boolean_endpoint_response(query)
    # print "\t{:20}: {}".format("LINKSET SIZE AFTER", Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, label)))
    # print "INSERTED STATUS: {}".format(inserted)
    # # print "TRIPLE COUNT: {}".format(count_triples("{0}{1}".format(Ns.linkset, label)))


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
            ?cluster ll:hasReference  \"{1}\" .
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


def property_builder(properties):

    rsc_plan = Buffer.StringIO()
    bind_plan = Buffer.StringIO()
    filter_plan = Buffer.StringIO()
    filter_plan.write("\n\t\tFILTER( ")
    compatibility = []
    pattern_count = 0
    for n in range(0, len(properties)):

        checked = Ut.split_property_path(properties[n])
        # print "\nPROPERTY {}\t".format(n, properties[n])
        # for item in checked:
        #     print "\t", item

        compatible = False
        if len(checked) not in compatibility:
            compatibility += [len(checked)]
            compatible = True

        if len(checked) == 1:

            if compatible is True:

                if rsc_plan.getvalue():
                    rsc_plan.write("\n\t\t\tUNION {{ ?resource ?prop_{}_0 ?value . }}".format(n))

                else:
                    rsc_plan.write("\n\t\t\t{{ ?resource ?prop_{}_0 ?value . }}".format(n))
                bind_plan.write("""\n\t\t\tBIND( CONCAT( "<", STR(?prop_{0}_0 ), ">" )  AS ?pattern_{1} ) """.format(
                    n, pattern_count))

                bind_plan.write("""\n\t\t\tBIND ( IRI(?pattern_{1}) AS ?prop_uri_{0} )""".format(n, pattern_count))

                pattern_count += 1

        else:

            for i in range(0, len(checked)):

                # START OF THE LOOP
                if i == 0:
                    # EXTRACTING THE PROPERTY PATH COMPOSITION IF ANY
                    if compatible is True:
                        if rsc_plan.getvalue():
                            rsc_plan.write("\n\t\t\t UNION {{ \n\t?resource ?prop_{0}_{1} ?object_{0}_{1} .".format(
                                n, i))
                        else:
                            rsc_plan.write("\n\t\t\t{{ ?resource ?prop_{0}_{1} ?object_{0}_{1} .".format(n, i))
                        # BINDING THE PROPERTY PATH FOR AS A STRING LATER USE FOR FILTERING
                        bind_plan.write("""\n\t\t\tBIND( CONCAT( "<", STR(?prop_{0}_{1})""".format(n, i))

                # END OF THE LOOP
                elif i == len(checked) - 1:
                    if compatible is True:
                        rsc_plan.write("\n\t\t\t?object_{0}_{1} ?prop_{0}_{2} ?value . }}".format(n, i-1, i))
                        bind_plan.write(""", ">/<", STR(?prop_{1}_{2}), ">") AS ?pattern_{1} )""".format(
                            checked[i], n, i))
                        bind_plan.write("""\n\t\t\tBIND ( IRI(?pattern_{0}) AS ?prop_uri_{0} )""".format(n))

                # MIDDLE OF THE LOOP
                else:
                    if compatible is True:
                        rsc_plan.write("\n\t?object_{0}_{1} ?prop_{0}_{2} ?object_{0}_{2} .".format(n, i-1, i))
                        bind_plan.write(""", ">/<", STR(?prop_{1}_{2}) """.format(checked[i], n, i))

    # USING THE EXTRACTED PATH FOR FILTERING
    property_list = ""
    for i in range(0, len(compatibility)):
        # print "Pattern: {}".format(compatibility[i])

        for n in range(0, len(properties)):
            checked = Ut.split_property_path(properties[n])
            if len(checked) == compatibility[i]:
                # print "yes"

                if i == 0:
                    value = """prop_uri_{}""".format(i)
                    if property_list.__contains__(value) is False:
                        property_list += """?prop_uri_{}""".format(i)
                    if n == 0:
                        filter_plan.write("""?pattern_{0} = STR(?prop_{1})""".format(i, n))
                    else:
                        filter_plan.write(""" || ?pattern_{0} = STR(?prop_{1})""".format(i, n))
                else:
                    property_list += """, ?prop_uri_{}""".format(i)
                    filter_plan.write(""" || ?pattern_{0} = STR(?prop_{1})""".format(i, n))

    filter_plan.write(" )")
    # print "\nPlan:", rsc_plan.getvalue()
    # print "\nCompatibility:", len(compatibility)
    # print "\nBind plan:", bind_plan.getvalue()
    # print "\nFiler plan:", filter_plan.getvalue()

    return [rsc_plan.getvalue(), bind_plan.getvalue(), filter_plan.getvalue(), property_list]

# TODO ADD THE DIFFERENCE => FILTER NOT EXISTS
# TODO MERGING CLUSTER
# TODO stardog-admin query list
# TODO stardog-admin query kill 66

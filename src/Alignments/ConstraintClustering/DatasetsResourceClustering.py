import Alignments.NameSpace as Ns
import Alignments.Utility as Ut
import Alignments.Query as Qry
import Alignments.Settings as St
import cStringIO as Buffer
import datetime
import time
import re
from Alignments.GenericMetadata import cluster_2_linkset_metadata as metadata
import Alignments.Server_Settings as Ss
from Alignments.Linksets.Linkset import writelinkset
DIRECTORY = Ss.settings[St.linkset_Exact_dir]


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
# print "\n{:>80}\n".format(datetime.datetime.today().strftime(_format))


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
    PREFIX void: <{3}>
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
    }} """.format(Ns.alivocab, Ns.prov, cluster_uri, Ns.void)
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


# PROPERTY REWRITING
def property_builder(properties, resource="resource", rs_object="value", tab_count=3, prop_id=""):

    rsc_plan = Buffer.StringIO()
    bind_plan = Buffer.StringIO()
    filter_plan = Buffer.StringIO()
    filter_plan.write("\n\t\t\t\tFILTER( ")
    compatibility = []
    pattern_count = 0

    tabs = ""
    for i in range(0, tab_count):
        tabs += "\t"

    string_bind = ""

    def checking(uri):
        checks = Ut.split_property_path(uri)
        if not checks:
            checks = re.findall("<([^<>]*)>*", uri)
        if not checks:
            checks = re.findall("(http[^<> ]*)", uri)
        return checks

    for n in range(0, len(properties)):

        property_checked = "{}".format(
            properties[n]) if Ut.is_nt_format(properties[n]) else "<{}>".format(properties[n])
        string_bind += """BIND("{}" AS ?prop{}_{})""".format(property_checked, prop_id, n) if n == 0 \
            else """\n{}BIND("{}" AS ?prop{}_{})""".format(tabs, property_checked, prop_id, n)

        checked = checking(properties[n])

        # print "\nPROPERTY {}\t".format(n, properties[n])
        # for item in checked:
        #     print "\t", item
        # print "\tPATTERN SIZE IS: ", len(checked)

        # COMPATIBLE CHECKS WHETHER WE HAVE DIFFERENT TRIPLE PATTERN
        # IF YES, A NEW PATTERN IS BUILT
        # PS; THIS WORKS ONLY FOR SEQUENCE PATTERN
        compatible = False

        if len(checked) not in compatibility:
            compatibility += [len(checked)]
            compatible = True

        if len(checked) == 1:

            if compatible is True:

                if rsc_plan.getvalue():
                    rsc_plan.write("\n{}UNION {{ ?{} ?prop{}_{}_0 ?{} . }}".format(
                        tabs, resource, prop_id, n, rs_object))
                else:
                    rsc_plan.write("\n{}{{ ?{} ?prop{}_{}_0 ?{} . }}".format(
                        tabs, resource, prop_id, n, rs_object))

                bind_plan.write("""\n{2}BIND( CONCAT( "<", STR(?prop{3}_{0}_0 ), ">" )  AS ?pattern{3}_{0} ) """.format(
                    n, pattern_count, tabs, prop_id))

                bind_plan.write("""\n{1}BIND ( IRI(?pattern{2}_{0}) AS ?prop{2}_uri_{0} )\n""".format(
                    n, tabs, prop_id))

                pattern_count += 1

        else:

            for i in range(0, len(checked)):

                # START OF THE LOOP
                if i == 0:

                    # EXTRACTING THE PROPERTY PATH COMPOSITION IF ANY
                    if compatible is True:
                        if rsc_plan.getvalue():
                            rsc_plan.write("\n{3}UNION {{ ?{0} ?prop{4}_{1}_{2} ?object{4}_{1}_{2} .".format(
                                resource, n, i, tabs, prop_id))
                        else:
                            rsc_plan.write("\n{3}{{ ?{0} ?prop{4}_{1}_{2} ?object{4}_{1}_{2} .".format(
                                resource, n, i, tabs, prop_id))

                        # BINDING THE PROPERTY PATH FOR AS A STRING LATER USE FOR FILTERING
                        bind_plan.write("""\n{2}BIND( CONCAT( "<", STR(?prop{3}_{0}_{1})""".format(n, i, tabs, prop_id))

                # END OF THE LOOP
                elif i == len(checked) - 1:

                    if compatible is True:
                        rsc_plan.write(
                            "\n{4}?object{5}_{0}_{1} ?prop{5}_{0}_{2} ?{3} . }}".format(
                                n, i-1, i, rs_object, tabs, prop_id))

                        bind_plan.write(""", ">/<", STR(?prop{3}_{1}_{2}), ">") AS ?pattern{3}_{1} )""".format(
                            checked[i], n, i, prop_id))

                        bind_plan.write("""\n{1}BIND ( IRI(?pattern{2}_{0}) AS ?prop{2}_uri_{0} )\n""".format(
                            n, tabs, prop_id))

                # MIDDLE OF THE LOOP
                else:
                    if compatible is True:
                        rsc_plan.write("\n\t?object{3}_{0}_{1} ?prop{3}_{0}_{2} ?object{3}_{0}_{2} .".format(
                            n, i-1, i, prop_id))

                        bind_plan.write(""", ">/<", STR(?prop{3}_{1}_{2}) """.format(checked[i], n, i, prop_id))

    # print string_bing

    # USING THE EXTRACTED PATH FOR FILTERING
    property_list = ""
    property_list_unique = []
    for i in range(0, len(compatibility)):
        # print "Pattern: {}".format(compatibility[i])

        for n in range(0, len(properties)):

            checked = checking(properties[n])
            if len(checked) == compatibility[i]:
                # print "yes"

                result = """?prop{}_uri_{}""".format(prop_id, i)
                if result not in property_list_unique:
                    property_list_unique += [result]

                if i == 0:
                    if property_list.__contains__(result) is False:
                        property_list += result
                    if n == 0:
                        filter_plan.write("""?pattern{2}_{0} = STR(?prop{2}_{1})""".format(i, n, prop_id))
                    else:
                        filter_plan.write(""" || ?pattern{2}_{0} = STR(?prop{2}_{1})""".format(i, n, prop_id))
                else:
                    result = """?prop{}_uri_{}""".format(prop_id, i)
                    property_list += """, {}""".format(result)
                    filter_plan.write(""" || ?pattern{2}_{0} = STR(?prop{2}_{1})""".format(i, n, prop_id))

    filter_plan.write(" )")
    # print "\nPlan:", rsc_plan.getvalue()
    # print "\nCompatibility:", len(compatibility)
    # print "\nBind plan:", bind_plan.getvalue()
    # print "\nFiler plan:", filter_plan.getvalue()

    return [rsc_plan.getvalue(), bind_plan.getvalue(),
            filter_plan.getvalue(), property_list, string_bind, property_list_unique]


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    [CREATING] A SINGLE CLUSTER OR MULTIPLE CLUSTERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# GIVEN A CONSTRAINT, CREATE A CLUSTER AND ADD RESOURCES FROM A SELECTED DATASET
# WHENEVER ITS RESOURCES SATISFIES THE CLUSTER'S CONSTRAINTS PROVIDED
def create_cluster(cluster_constraint, dataset_uri, property_uri, count=1,
                   reference=None, group_name=None, strong=True, activated=False):

    """
    :param cluster_constraint: a ascii string to satisfy for example country name: BENIN
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI for which the constraints are evaluated against.
    :param count: just an int for counting the number of clusters
    :param reference: name associated to a group of clusters
    :param activated: boolean value for activating the function
    :param group_name: the label for the reference
    :param strong: reuse existing cluster or create new cluster
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
        print "\tTHE FUNCTION IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED", St.result: None, 'group_name': None, "reference": None}

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

    label = Ut.prep_4_uri(constraint)

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

    second_code = Ut.hash_it(constraint)[:10]
    if reference is None:
        ref_code = Ut.hash_it("{}".format(datetime.datetime.today().strftime(_format)))
        reference = "{}reference/{}".format(Ns.cluster, ref_code)
        comment_ref = ""
        comment_ref_2 = "#"

    else:
        comment_ref = "#"
        comment_ref_2 = ""
        ref_code = Ut.get_uri_local_name(reference)

    if strong is True:
        strong_append = "#"
    else:
        strong_append = ""

    concat_code = "{}_{}".format(ref_code, second_code)

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
            {13}?insertGraphURI  rdfs:label  ""\"{22}\""" .

            # 2. THE REFERENCE LABEL
            ?cluster_ref  rdfs:label  \"{6}\" .

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
        BIND( CONCAT("{1}", "{23}", "_", "{2}") AS ?insertGraph )
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
                # THE REFERENCE
                {21}{12}?insertGraphURI  ll:hasReference  ?cluster_ref .
                {21}{13}?insertGraphURI  ll:hasReference  <{14}> .

                # 3. THE CONSTRAINT
                ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .

                # 4. CONSTRAINT'S METADATA
                ?URL_CONSTRAINT  ll:hasValue  ?constraint .
                ?URL_CONSTRAINT  void:target  <{3}> .
                #MAKING STRICTER BY INCLUDING THE PROPERTIES TO THE RESTRICTION  {19} .
            }}
        }}
    }}
    """.format(
        # 0          1           2      3            4              5             6           7
        Ns.alivocab, Ns.cluster, label, dataset_uri, property_list, constraint_v, group_name, Ns.prov,
        # 8                    9           10          11              12          13             14         15
        Ns.cluster_constraint, Ns.cluster, plans[3], property_bind, comment_ref, comment_ref_2, reference, Ns.void,
        # 16      17        18        19     20        21             22          23
        plans[0], plans[1], plans[2], fetch, ref_code, strong_append, constraint, concat_code
    )
    # print query

    query_strong_true = """
    PREFIX ll: <{0}>
    PREFIX prov: <{7}>
    PREFIX void: <{15}>
    INSERT
    {{
        # THE CLUSTERED GRAPH
        GRAPH ?cluster
        {{
            # 1. THE REFERENCE
            {12}?cluster  ll:hasReference  ?cluster_ref .
            {13}?cluster  ll:hasReference  <{14}> .

            # 2. THE REFERENCE LABEL
            ?cluster_ref  rdfs:label  \"{6}\" .

            # 3. THE CONSTRAINT
            ?insertGraphURI  ll:hasConstraint  ?URL_CONSTRAINT .

            # 4. CONSTRAINT'S METADATA
            ?URL_CONSTRAINT  ll:hasValue  ?constraint .
            ?URL_CONSTRAINT  void:target  <{3}> .
            ?URL_CONSTRAINT  ll:hasProperty  {10} .

            # 5. THE LIST OR RESOURCES
            ?cluster  ll:list  ?resource .
        }}
    }}
    WHERE
    {{
        # NAME
        BIND( "{20}" AS ?code)

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
        {{
            GRAPH ?cluster
            {{
                # 3. THE CONSTRAINT
                ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .

                # 4. CONSTRAINT'S METADATA
                ?URL_CONSTRAINT  ll:hasValue  ?constraint .
                ?URL_CONSTRAINT  void:target  <{3}> .
                #MAKING STRICTER BY INCLUDING THE PROPERTIES TO THE RESTRICTION  {19} .
            }}
        }}
    }}
    """.format(
        # 0          1           2      3            4              5             6           7
        Ns.alivocab, Ns.cluster, label, dataset_uri, property_list, constraint_v, group_name, Ns.prov,
        # 8                    9           10          11              12          13             14         15
        Ns.cluster_constraint, Ns.cluster, plans[3], property_bind, comment_ref, comment_ref_2, reference, Ns.void,
        # 16      17        18        19     20        21
        plans[0], plans[1], plans[2], fetch, ref_code, strong_append
    )
    # print query_strong_true

    # return {St.message: "THE CLUSTER WAS SUCCESSFULLY EXECUTED.",
    #         St.result: "", 'group_name': group_name}

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    Qry.boolean_endpoint_response(query)

    # FETCH THE CLUSTER REFERENCE URL
    reference_query = """
    PREFIX ll: <{0}>
    PREFIX prov: <{1}>
    PREFIX void: <{7}>
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
    """.format(Ns.alivocab, Ns.prov, dataset_uri, fetch, Ns.cluster, concat_code, label, Ns.void)
    # print "reference_query:", reference_query

    # RUN FETCH
    reference_response = Qry.sparql_xml_to_matrix(reference_query)
    # print "reference_response:", reference_response

    reference_result = reference_response[St.result]
    # print "reference_result:", reference_result

    print "\n\tCLUSTER {}: {}".format(count, "{}{}_{}".format(Ns.cluster, concat_code, label))
    print "\t\t{:19} : {}".format("REFERENCE CODE", ref_code)
    print "\t\t{:19} : {}".format("CONSTRAINT", constraint)
    print "\t\t{:19} : {}".format("GROUP NAME", group_name)
    print "\t\t{:19} : {}".format("REFERENCE", reference)
    if reference_result:
        print "\t\t{:19} : {}".format("Nbr OF REFERENCES", len(reference_result) - 1)
    print "\t\t{:19} : {}".format("CLUSTER SIZE", count_list("{}{}_{}".format(Ns.cluster, concat_code, label)))

    print "\t\t{:19} : {}".format("DERIVED FROM", dataset_uri)

    if strong is True:

        Qry.boolean_endpoint_response(query_strong_true)

        # FETCH THE CLUSTER REFERENCE URL
        reference_query = """
        PREFIX ll: <{0}>
        PREFIX prov: <{1}>
        PREFIX void: <{4}>
        SELECT DISTINCT ?cluster_ref ?cluster
        {{
            # CONSTRAINT VALUES
            VALUES ?constraint {{ {5} }}
            # THE CLUSTERED GRAPH
            GRAPH ?cluster
            {{
                # 1. THE REFERENCE
                ?cluster  ll:hasReference  ?cluster_ref .

                # 3. THE CONSTRAINT
                ?cluster  ll:hasConstraint  ?URL_CONSTRAINT .

                # 4. CONSTRAINT'S METADATA
                ?URL_CONSTRAINT  ll:hasValue  ?constraint .
                ?URL_CONSTRAINT  void:target  <{2}> .
                {3}
            }}
        }}
        """.format(Ns.alivocab, Ns.prov, dataset_uri, fetch, Ns.void, constraint_v)
        # print "reference_query:", reference_query

        # RUN FETCH
        reference_response = Qry.sparql_xml_to_matrix(reference_query)
        # print "reference_response:", reference_response

        reference_result = reference_response[St.result]
        # print "reference_result:", reference_result

        if reference_result:
            print "\n\tADDING TO THE EXISTING OLD CLUSTER INSTEAD"
            print "\t\t{:19} : {}".format("OLD CLUSTER", reference_result[1][1])
            print "\t\t{:19} : {}".format("OLD REFERENCE CODE", Ut.extract_ref(reference_result[1][1]))
            print "\t\t{:19} : {}".format("CONSTRAINT", constraint)
            print "\t\t{:19} : {}".format("GROUP NAME", group_name)
            print "\t\t{:19} : {}".format("REFERENCE", reference)
            print "\t\t{:19} : {}".format("Nbr OF REFERENCES", len(reference_result) - 1)
            print "\t\t{:19} : {}".format("CLUSTER SIZE", count_list("{}".format(reference_result[1][1])))
            print "\t\t{:19} : {}".format("DERIVED FROM", dataset_uri)

    return {St.message: "THE CLUSTER WAS SUCCESSFULLY EXECUTED.",
            St.result: reference_result, 'group_name': group_name, "reference": reference}


# GENERATE MULTIPLE CLUSTERS FROM AN INITIAL DATASET
def create_clusters(initial_dataset_uri, property_uri,
                    reference=None, group_name=None, not_exists=False, strong=True, activated=False):

    # IF THE REFERENCE IS NONE OR NOT GIVEN,
    # A REFERENCE IS GENERATED IN THE FIRST ITERATION OF THIS FUNCTION

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
        print "\tTHE FUNCTION IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED", "reference": ""}

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
    Qry.display_matrix(constraint_table_response, is_activated=True, limit=5)

    if constraint_table is None:
        print "NO CONSTRAINT COULD BE FOUND"
        return {St.message: "NO CONSTRAINT COULD BE FOUND", "reference": reference}

    reference_uri = ""
    for i in range(1, len(constraint_table)):

        # print "Count runs: ", i

        if i == 1:
            response = create_cluster(
                constraint_table[i], initial_dataset_uri, property_uri, count=i,
                reference=reference, group_name=group_name, strong=strong, activated=True)
            # print "reference_uri_response:", response

            reference_uri = response["reference"]

        else:
            # print reference_uri
            create_cluster(constraint_table[i], initial_dataset_uri, property_uri, count=i,
                           reference=reference_uri, group_name=group_name, strong=strong, activated=True)

        # if i == 3:
        #     break

    # print "reference_uri:",

    if reference_uri:
        # server_message = "Cluster created as: {}".format(reference_uri)
        message = "The cluster was created as [{}] with {} clusters!".format(
            reference_uri, len(constraint_table) - 1)
        print message
        return {St.message: message, "reference": reference_uri, "group_name": group_name}

    return {St.message: "The cluster could not be created", "reference": None, "group_name": group_name}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    [ADDING] TO A SINGLE CLUSTER OR TO MULTIPLE CLUSTERS
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
        print "\tTHE FUNCTION IS NOT ACTIVATE"
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


def add_to_cluster(cluster_uri, reference, dataset_uri, property_uri, count=1, activated=False):

    """
    :param cluster_uri: the cluster graph
    :param dataset_uri: the dataset URI
    :param property_uri: the property URI
    :param count: just an int for counting the number of clusters
    :param activated: boolean value for activating the function
    :param reference: the reference of the cluster
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
        print "\tTHE FUNCTION IS NOT ACTIVATED"
        return "THE FUNCTION IS NOT ACTIVATED"

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
            label = Ut.prep_4_uri(Ut.get_uri_local_name(property_list))

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

                    # 2. THE REFERENCE LABEL
                    <{11}>  rdfs:label  \"{12}\" .

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
                # 6                    7           8           9              10       11         12
                Ns.cluster_constraint, Ns.cluster, properties, property_bind, Ns.void, reference, label)
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
        return {St.message: "AS THE REFERENCE IS NOT PROVIDED, THE PROCESS WAS TERMINATED.", "reference": None}

    # FUNCTION ACTIVATION
    if activated is False:
        print "\tTHE FUNCTION IS NOT ACTIVATED"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED", "reference": None}

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

        Qry.display_matrix(cluster_table_response, limit=5, is_activated=True)
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
            add_to_cluster(cluster_table[i][0], reference, dataset_uri, property_uri, count=i, activated=True)

            # if i == 3:
            #     break

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
    CREATING A [LINKSET] OUT OF A CLUSTERS OR OUT OF
            CLUSTERS THAT SAME REFERENCE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


# HELPING IN GENERATING THE LINKSET FROM CLUSTER METADATA
def helper(specs, is_source=True):

    def property_list(properties_uri):
        values = ""
        # MAKING SURE THAT THE PROPERTIES URI ARE IN ANGLE BRACKETS
        for j in range(0, len(properties_uri)):
            if Ut.is_nt_format(properties_uri[j]) is False:
                properties_uri[j] = "<{}>".format(properties_uri[j])
            if j == 0:
                values = "({})".format(properties_uri[j])

            else:
                values += "\n\t\t\t\t\t | ({})".format(properties_uri[j])
        return values

    if is_source is True:
        number = 1
    else:
        number = 2
    builder = Buffer.StringIO()
    is_empty = True

    singleton = """

                    ### Create A SINGLETON URI"
                    BIND( replace("{0}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
                    BIND( iri(?pre) as ?singPre )""".format(Ns.alivocab)
    if number == 2:
        singleton = ""

    insert_prop = []

    for dataset in specs:
        graph = dataset[St.graph]
        data = dataset[St.data]

        for detail in data:
            properties = detail[St.properties]
            re_wright = property_builder(
                properties, "resource_{}".format(number), "obj_{}".format(number), 5, str(number))

            pattern = re_wright[0]
            pattern_bind = re_wright[1]
            string_bind = re_wright[4]
            p_filter = re_wright[2]
            for prop in re_wright[5]:
                if prop not in insert_prop:
                    insert_prop += [prop]

            union = "\n\t\t\t\tUNION " if is_empty is False else ""
            sub = """{3}{{
                BIND(<{2}#copy> AS ?datasetCopy_{0})
                BIND(<{2}> AS ?dataset_{0})
                ?resource_{0} {1} ?obj_{0} .

                #?resource_{0} ?property_{0} ?obj_{0} .
                {6}
                {7}

                {8}
                # TO STRING AND TO LOWER CASE
                BIND(lcase(str(?obj_{0})) as ?label_{0})

                # VALUE TRIMMING
                BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
                BIND(REPLACE(?label_{0}, ?regexp, '$1$2') AS ?trimmed_label){5}
                {9}
            }} """.format(number, property_list(properties), graph, union, Ns.alivocab, singleton,
                          string_bind, pattern, pattern_bind, p_filter)
            is_empty = False

            builder.write(sub)

    # # FIND SOME INFORMATION ABOUT RESOURCE_O WITHIN A RANDOM GRAPH {0}
    query = """GRAPH ?datasetCopy_{0}
        {{
            {1}
        }}
    """.format(number, builder.getvalue())
    # print query

    insert_list = ""
    for i in range(0, len(insert_prop)):
        insert_list += insert_prop[i] if i == 0 else ", {}".format(insert_prop[i])
    # print insert_list

    return {"query": query, "insert_list": insert_list}


# GENERATE AN EXACT MATCH LINKSET FROM A CLUSTER
def linkset_from_cluster(specs, cluster_uri, user_label=None, count=1, activated=False):

    # FUNCTION ACTIVATION
    if activated is False:
        print "\tTHE FUNCTION IS NOT ACTIVATED"
        return "THE FUNCTION IS NOT ACTIVATED"

    values = ""
    constraints = ""
    # print cluster_uri

    # EXTRACTING THE CLUSTER METADATA MEANING DATASETS AND CONSTRAINTS
    cluster_metadata = cluster_meta(cluster_uri)
    dataset_count = len(cluster_metadata['datasets'])
    c_metadata = cluster_metadata['constraints']

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
    for item in c_metadata:
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
    # specs[St.targets] IS A LIST OF DICTIONARIES WITH St.graph AND St.data as KEYS
    # St.data IS AN OTHER LIST OF DICTIONARY WITH St.entity_datatype AND St.properties KEYS
    # WHERE St.properties IS A LIST OF PROPERTIES
    targets_array = specs[St.targets]
    # targets = ""
    # for i in range(0, len(targets_array)):
    #
    #     if i == 0:
    #         targets = "<{}>".format((targets_array[i])[St.graph])
    #     else:
    #         targets += " ,\n\t\t\t\t\t\t\t\t\t\t\t<{}>".format((targets_array[i])[St.graph])

    # A TARGET COMBINES A DATATYPE AND A LIST OF PROPERTIES
    # alignment_targets = target_datatype_properties(targets_array, "alignmentTarget", label)

    # {"query": query, "insert_list": insert_list}
    re_writer_1 = helper(targets_array, is_source=True)
    re_writer_2 = helper(targets_array, is_source=False)

    query = """
    # CREATION OF A LINKSET OF MIXED-RESOURCES
    PREFIX ll:          <{0}>
    PREFIX void:        <{6}>
    PREFIX rdfs:        <{7}>
    PREFIX bdb:         <{8}>
    PREFIX prov:        <{9}>
    PREFIX singleton:   <{10}>
    prefix linkset:     <{3}>
    PREFIX llTarget:    <{11}>
    prefix stardog:     <tag:stardog:api:context:>
    INSERT
    {{
        GRAPH singleton:{4}
        {{
            ?singPre ll:hasStrength         1 .
            ?singPre ll:hasEvidence         ?trimmed_label .
            ?singPre void:subjectsTarget    ?dataset_1 .
            ?singPre void:objectsTarget     ?dataset_2 .
            ?singPre ll:alignsSubjects      {12} .
            ?singPre ll:alignsObjects       {13} .
        }}

        GRAPH linkset:{4}
        {{
            ?resource_1  ?singPre ?resource_2 .
        }}
    }}
    WHERE
    {{
        # TAKE 2 RANDOM RESOURCES FROM THE CLUSTER
        GRAPH <{1}>
        {{
            <{1}> ll:list ?resource_1 .
            <{1}> ll:list ?resource_2 .
        }}
        # FIND SOME INFORMATION ABOUT RESOURCE_O WITHIN A RANDOM GRAPH 1
        {2}
        # FIND THE SAME INFORMATION ABOUT RESOURCE_1 WITHIN A DIFFERENT RANDOM GRAPH 2
        {5}
        #FILTER(str(?dataset_1) > str(?dataset_2))
        FILTER(str(?resource_1) > str(?resource_2))
    }}
    """.format(Ns.alivocab, cluster_uri, re_writer_1["query"],
               Ns.linkset, label, re_writer_2["query"],
               # 6      7        8       9        10             11
               Ns.void, Ns.rdfs, Ns.bdb, Ns.prov, Ns.singletons, Ns.alignmentTarget,
               # 12                        13
               re_writer_1["insert_list"], re_writer_2["insert_list"])
    # print query

    print "\nRUN {}: {}".format(count, cluster_uri)
    print "\t{:20}: {}".format("CLUSTER SIZE ", Qry.get_namedgraph_size(cluster_uri))
    print "\t{:20}: {}".format("STARTED ON", datetime.datetime.today().strftime(_format))
    print "\t{:20}: {}".format("LINKSET", label)
    print "\t{:20}: {}".format("LINKSET SIZE BEFORE", Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, label)))

    # FIRE THE CONSTRUCT AGAINST THE TRIPLE STORE
    start = time.time()
    Qry.boolean_endpoint_response(query)
    end = time.time()
    diff = end - start

    print "\t{:20}: {}".format("ENDED ON", datetime.datetime.today().strftime(_format))
    size_after = Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, label))
    print "\t{:20}: {}".format("LINKSET SIZE AFTER", size_after)
    print "\t{:20}: {} ".format(">>> Executed in", str(datetime.timedelta(seconds=diff)))

    specs[St.triples] = size_after
    return {St.message: "The linkset was created as [{}] and contains {} triples".format(
        label, size_after), St.result: label, "correspondences": size_after}


# FROM MULTIPLE CLUSTERS TO A SINGLE MULTI SOURCES LINKSET
def linkset_from_clusters(specs, activated=False):

    print "\n>>> CREATING A MIXED RESOURCES-LINKSET\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # FUNCTION ACTIVATION
    if activated is False:
        print "\tTHE FUNCTION IS NOT ACTIVATED"
        return "THE FUNCTION IS NOT ACTIVATED"

    # EXTRACT ALL CLUSTERS THAT SHARE THE SAME INITIAL DATASET THERE ARE DERIVED FROM
    query = """
    # FIND A CLUSTER FOR WITCH YOU SHARE THE SAME CONSTRAINT
    PREFIX ll: <{0}>
    SELECT ?cluster
    {{
        GRAPH ?cluster
        {{
            ?cluster ll:hasReference  <{1}> .
        }}
    }}
    """.format(Ns.alivocab, specs[St.reference])
    # print query

    # RUN THE QUERY AGAINST  THE TRIPLE STORE
    cluster_table_response = Qry.sparql_xml_to_matrix(query)
    cluster_table = cluster_table_response[St.result]

    # DISPLAY A SAMPLE OF THE TABLE
    print "\t>>> TABLE OF COMPATIBLE CLUSTER(S) FOUND"
    Qry.display_matrix(cluster_table_response, limit=5, is_activated=True)
    # print "cluster_table:", cluster_table_response

    if cluster_table is None:
        print "NO LINKSET COULD BE GENERATED AS NO MATCHING CLUSTER COULD BE FOUND."
        return "NO LINKSET COULD BE GENERATED AS NO MATCHING CLUSTER COULD BE FOUND."

    # BUILD THE STRING FOR GENERATING THE MIXED RESOURCE LINKSET
    builder = Buffer.StringIO()
    for i in range(1, len(cluster_table)):
        builder.write(" {}".format(cluster_table[i]))

    # LINKSET LABEL (ID)
    # identification = hash(builder.getvalue())
    # label = "clustered_{}".format(str(identification).replace("-", "N")) \
    #     if str(identification).startswith("-") else "clustered_P{}".format(str(identification))
    # label = specs[St.linkset_name]
    # print label

    # CREATE AND ADD RESOURCES TO THE LINKSET
    result = {St.message: "The linkset was not created.", St.result: None}
    linkset_name = specs[St.linkset_name]

    # DATASET SUBSET COPY: MAKE A COPY OF THE DATASETS TO IMPROVE EFFICIENCY
    print ""
    drop_count = 0
    drop_dataset_copies = ""
    for dataset in specs[St.targets]:

        triples_insert = ""
        triples_where = ""
        graph = dataset[St.graph]
        if drop_count == 0:
            drop_dataset_copies = "DROP SILENT GRAPH <{}#copy>".format(graph)
        else:
            drop_dataset_copies += ";\nDROP SILENT GRAPH <{}#copy>".format(graph)

        # print graph
        data = dataset[St.data]

        count = 0
        for detail in data:
            properties = detail[St.properties]
            for property in properties:
                count += 1
                # print "\t {}".format(property)
                triples_insert += "\n\t\t\t?subject {} ?value_{} .".format(property, count)
                triples_where += "\n\t\t\tOptional {{ ?subject {} ?value_{} }} .".format(property, count)

        query_copy = """
    INSERT
    {{
        GRAPH <{0}#copy>
        {{{1}
        }}
    }}
    WHERE
    {{
        GRAPH <{0}>
        {{
            ?subject a ?type .{2}
        }}
    }}
    """.format(graph, triples_insert, triples_where)
        # print query_copy
        print "\nDROP THE DATASET COPIES IF EXISTS: ", graph
        print Qry.boolean_endpoint_response("DROP SILENT GRAPH <{}#copy>".format(graph))
        print "COPY: ", graph
        print Qry.boolean_endpoint_response(query_copy)
        drop_count += 1


    correspondences = 0
    for i in range(1, len(cluster_table)):
        result = linkset_from_cluster(specs, cluster_table[i][0], linkset_name, count=i, activated=activated)
        correspondences += int(result["correspondences"])
        # if i == 10:
        #     break

    if correspondences > 0:
        print "\nINSERTING THE GENERIC METADATA AS A TOTAL OF {} CORRESPONDENCE(S) WERE INSERTED.".format(
            correspondences)
        metadata(specs)

        src = ["source", "", "entity_ns"]
        trg = ["target", "graph_name", "", "St.entity_ns"]
        linkset_path = DIRECTORY
        writelinkset(src, trg, specs[St.linkset_name], linkset_path, specs["metadata"])

    print "\nDROP THE DATASET COPIES"
    print drop_dataset_copies
    print Qry.boolean_endpoint_response(drop_dataset_copies)

    return result


# TODO ADD THE DIFFERENCE => FILTER NOT EXISTS
# TODO MERGING CLUSTER
# TODO stardog-admin query list
# TODO stardog-admin query kill 66


# MATRIX
# http://complexitylabs.io/course/network-theory/
# http://complexitylabs.io/course/network-theory/?course_type=content&course_page=1&lecture=1&section-quiz=1

# CENTRALITY:

#   THE IMPORTANCE OF A NODE OR SIGNIFICANCE OF A NODE
#   THE POSITION OF THE NODE

#       DEGREE OF CONNECTIVITY
#       ======================
#       measure of the number of in and out links the node has to other nodes
#
#       CLOSENESS
#       =========
#       HOW LONG WILL IT TAKE TO SPREAD GOSSIP?
#       the sum of the length of the shortest paths between the node and all other nodes in the graph.
#       Thus the more central a node is, the closer it is to all other nodes.
#
#       BETWEENESS
#       ==========
#       NODES THAT HAVE A HIGH PROBABILITY OF OCCURRING ON A RANDOM CHOSEN SHORTEST PATH BETWEEN TWO NODES.
#       it represents the degree of which nodes stand between each other.
#       For every pair of vertices in a connected graph, there exists at least one shortest path between
#       the vertices such that either the number of edges that the path passes through (for unweighted graphs)
#       or the sum of the weights of the edges (for weighted graphs) is minimized. The betweenness centrality
#       for each vertex is the number of these shortest paths that pass through the vertex.
#
#       PRESTIGE
#       ========
#
# CHECK

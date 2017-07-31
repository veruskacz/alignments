import Alignments.NameSpace as Ns
from Alignments.Query import boolean_endpoint_response, sparql_xml_to_matrix

def update_evidence(singleton_uri, message, research_uri, accepted=True):
    """
    This function is called due to request /updateevidence
    It updates a singleton property resource with the validation info.
    The results, ...,
    """

    predicate = "{}{}".format(Ns.alivocab, "hasValidation")
    hash_val = hash(singleton_uri + research_uri)
    hash_val = str(hash_val).replace("-", "N") if str(hash_val).__contains__("-") else "P{}".format(hash_val)
    validation_uri = "{}validation_{}".format(Ns.risis, hash_val)
    validation_type = "{}Accept".format(Ns.prov) if accepted else "{}Reject".format(Ns.alivocab)

    query = """
    PREFIX prov:<{8}>
    INSERT
    {{
    	GRAPH ?g
    	{{
    	    ### 1. CREATE A VALIDATION RESOURCE WITH A TYPE AND MESSAGE
            <{2}>
                a   <{3}> ;
                <{6}comment> \"\"\"{7}.\"\"\" .

            ### 2. LINK THE RESEARCH QUESTION TO THE VALIDATION
            <{5}>
                <{4}>   <{2}> .

            ### LINK THE SINGLETON TO THE VALIDATION RESOURCE
    	    <{0}>
                <{1}>   <{2}> .
    	}}
    }}
    WHERE
    {{
        {{
            GRAPH ?g
            {{
                # THE CURRENT TRIPLE FOR WHICH THE VALIDATION IS BEING CREATED
                {{ <{0}> ?p ?o . }}
                UNION
                # OTHER SINGLETON GRAPHS THAT DERIVED THERE TRIPLE FROM THE CURRENT SINGLETON
                {{ ?singleton prov:wasDerivedFrom <{0}> . }}
                FILTER NOT EXISTS
                {{
                    <{2}> ?PRE ?OBJ .
                }}
            }}
        }}
        UNION
        {{
            # OTHER SINGLETON GRAPHS FROM WHICH THE CURRENT SINGLETON WAS DERIVE FROM
            GRAPH ?gPrime
            {{
                <{0}> prov:wasDerivedFrom ?earlierSing .
            }}
            GRAPH ?g
            {{
                ?earlierSing ?p ?o .
                FILTER NOT EXISTS
                {{
                    <{2}> ?PRE ?OBJ .
                }}
            }}
        }}

    }}""".format(
        # 0            1          2               3                4
        singleton_uri, predicate, validation_uri, validation_type, "{}created".format(Ns.alivocab),
        # 5           6        7        8
        research_uri, Ns.rdfs, message, Ns.prov
    )






    query = """
    PREFIX prov:<{8}>

    # 1. THE CURRENT TRIPLE FOR WHICH THE VALIDATION IS BEING CREATED
    INSERT
    {{
    	GRAPH ?g
    	{{
    	    ### 1. CREATE A VALIDATION RESOURCE WITH A TYPE AND MESSAGE
            <{2}>  a  <{3}> ;
                <{6}comment> \"\"\"{7}.\"\"\" .

            ### 2. LINK THE RESEARCH QUESTION TO THE VALIDATION
            <{5}>  <{4}>  <{2}> .

            ### LINK THE SINGLETON TO THE VALIDATION RESOURCE
    	    <{0}>  <{1}>  <{2}> .
    	}}
    }}
    WHERE
    {{
        GRAPH ?g
        {{
            <{0}> ?p ?o .
            FILTER NOT EXISTS
            {{
                <{2}> ?PRE ?OBJ .
            }}
        }}
    }} ;

    # 2. FORWARD PROPAGATION: SINGLETON GRAPHS THAT DERIVED THERE TRIPLE FROM THE CURRENT SINGLETON
    INSERT
    {{
    	GRAPH ?g
    	{{
    	    ### 1. CREATE A VALIDATION RESOURCE WITH A TYPE AND MESSAGE
            <{2}>  a  <{3}> ;
                <{6}comment> \"\"\"{7}.\"\"\" .

            ### 2. LINK THE RESEARCH QUESTION TO THE VALIDATION
            <{5}>  <{4}>  <{2}> .

            ### LINK THE SINGLETON TO THE VALIDATION RESOURCE
    	    ?singleton  <{1}>  <{2}> .
    	}}
    }}
    WHERE
    {{
        GRAPH ?g
        {{
            ?singleton prov:wasDerivedFrom <{0}> .
            FILTER NOT EXISTS
            {{
                <{2}> ?PRE ?OBJ .
            }}
        }}
    }} ;

    # 3. BACKWARD PROPAGATION: SINGLETON GRAPHS FROM WHICH THE CURRENT SINGLETON WAS DERIVE FROM
    INSERT
    {{
    	GRAPH ?g
    	{{
    	    ### 1. CREATE A VALIDATION RESOURCE WITH A TYPE AND MESSAGE
            <{2}>  a  <{3}> ;
                <{6}comment> \"\"\"{7}.\"\"\" .

            ### 2. LINK THE RESEARCH QUESTION TO THE VALIDATION
            <{5}>  <{4}>  <{2}> .

            ### LINK THE SINGLETON TO THE VALIDATION RESOURCE
    	    ?earlierSing  <{1}>  <{2}> .
    	}}
    }}
    WHERE
    {{
        # OTHER
        GRAPH ?gPrime
        {{
            <{0}> prov:wasDerivedFrom ?earlierSing .
        }}
        GRAPH ?g
        {{
            ?earlierSing ?p ?o .
            FILTER NOT EXISTS
            {{
                <{2}> ?PRE ?OBJ .
            }}
        }}
    }}""".format(
        # 0            1          2               3                4
        singleton_uri, predicate, validation_uri, validation_type, "{}created".format(Ns.alivocab),
        # 5           6        7        8
        research_uri, Ns.rdfs, message, Ns.prov
    )









    response = None
    response = boolean_endpoint_response(query)
    print query
    print "\n\nUPDATE RESPONSE:", response

    return response


def register_correspondence_filter(research_uri, graph_uri, method, greater_eq=None, smaller_eq=None):

    # print research_uri, graph_uri, method, greater_eq, smaller_eq

    c_filter = ""
    filter_uri = ''

    if method == "threshold":
        if greater_eq is not None:
            c_filter = """\n\t\t\t\tFILTER (STRDT(str(?o), xsd:decimal) {}  {}) """.format(
                greater_eq["operator"], greater_eq["value"])

        if smaller_eq is not None:
            c_filter += """\n\t\t\t\tFILTER (STRDT(str(?o), xsd:decimal) {}  {})""".format(
                smaller_eq["operator"], smaller_eq["value"])

    elif method == "accept":
        condition = ""
        if greater_eq is not None:
            condition = """ count(distinct ?accept) {} {}""".format(greater_eq["operator"], greater_eq["value"])
        if smaller_eq is not None:
            condition += " && " if condition != "" else ""
            condition += """ count(distinct ?accept) {} {}""".format(smaller_eq["operator"], smaller_eq["value"])
        c_filter += "HAVING ({})".format(condition) if condition != "" else ""

    elif method == "reject":
        condition = ""
        if greater_eq is not None:
            condition = """ count(distinct ?reject) {} {}""".format(greater_eq["operator"], greater_eq["value"])
        if smaller_eq is not None:
            condition += " && " if condition != "" else ""
            condition += """ count(distinct ?reject) {} {}""".format(smaller_eq["operator"], smaller_eq["value"])
        c_filter += "HAVING ({})".format(condition) if condition != "" else ""

    if c_filter != "":
        hash_code = hash(research_uri + graph_uri + c_filter)
        hash_code = str(hash_code).replace("-", "N") if str(hash_code).__contains__("-") else "P{}".format(hash_code)
        filter_uri = "{}c_filter_{}".format(Ns.risis, hash_code)

    if filter_uri != '':
        query = """
    INSERT
    {{
        ### THE RESEARCH QUESTION CREATED A FILTER
        GRAPH <{0}>
        {{
            <{0}>
                <{1}created> <{2}> .

            <{2}>
                a   <{3}Filter> ;
                <{1}appliesTo>  <{4}> ;
                <{5}comment>    \"\"\"{6}\"\"\" ;
                <{1}method>  \"\"\"{7}\"\"\" .
        }}
    }}

    WHERE
    {{
        GRAPH <{0}>
        {{
            FILTER NOT EXISTS
            {{
                <{0}>
                    <{1}created> <{2}> .
            }}
        }}
    }}
    """.format(
            # 0           1            2           3           4            5        6         7
            research_uri, Ns.alivocab, filter_uri, Ns.riclass, graph_uri, Ns.rdfs, c_filter, method)
        print query

        # REGISTER IT
        response = boolean_endpoint_response(query)

    print 'Filter insertion ', response, filter_uri

    if response:
        return {'result': filter_uri}
    else:
        return {'result': None}

# replaced by get_graph_filter
# def get_linkset_filter(research_uri, graph_uri, filter_uri=''):
#
#     if filter_uri == '':
#         filter_uri = '?filter'
#     else:
#         filter_uri = '<'+filter_uri+'>'
#
#     query = """
#     SELECT ?comment ?method
#     {{
#         GRAPH <{0}>
#         {{
#             {4}
#                 a <{1}Filter> ;
#                 <{2}appliesTo>  <{3}> ;
#                 rdfs:comment ?comment ;
#                 <{2}method>  ?method .
#         }}
#     }}
#     """.format(research_uri, Ns.riclass, Ns.alivocab, graph_uri, filter_uri)
#
#     print query
#
#     result = sparql_xml_to_matrix(query)
#
#     return result

def get_graph_filter(research_uri, graph_uri, filter_uri=''):

    if filter_uri == '':
        filter_uri = '?filter'
    else:
        filter_uri = '<'+filter_uri+'>'

    query = """
    SELECT ?comment ?method
    {{
        GRAPH <{0}>
        {{
            {4}
                a <{1}Filter> ;
                <{2}appliesTo>  <{3}> ;
                rdfs:comment ?comment ;
                <{2}method>  ?method .
        }}
    }}
    """.format(research_uri, Ns.riclass, Ns.alivocab, graph_uri, filter_uri)

    print query

    result = sparql_xml_to_matrix(query)

    return result

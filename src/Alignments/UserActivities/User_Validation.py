import src.Alignments.NameSpace as Ns
from src.Alignments.Query import boolean_endpoint_response, sparql_xml_to_matrix

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
    INSERT
    {{
    	GRAPH ?g
    	{{
    	    ### 1. CREATE A VALIDATION RESOURCE WITH A TYPE AND MESSAGE
            <{2}>
                a   <{3}> ;
                <{6}comment> \"\"\"{7}\"\"\" .

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
        GRAPH ?g
        {{
            <{0}> ?p ?o
            FILTER NOT EXISTS
            {{
                <{2}> ?PRE ?OBJ .
            }}
        }}
    }}""".format(
        # 0            1          2               3                4
        singleton_uri, predicate, validation_uri, validation_type, "{}created".format(Ns.alivocab),
        # 5           6
        research_uri, Ns.rdfs, message
    )
    response = None
    response = boolean_endpoint_response(query)
    print query
    print "\n\nUPDATE RESPONSE:", response

    return response


def register_correspondence_filter(research_uri, linkset_uri, method, greater_eq=None, smaller_eq=None):

    c_filter = ""
    query = ""

    if method == "threshold":
        if greater_eq is not None:
            c_filter = """\n\t\t\t\tFILTER (STRDT(str(?o), xsd:integer) {}  {}) """.format(
                greater_eq["operator"], greater_eq["value"])

        if smaller_eq is not None:
            c_filter += """\n\t\t\t\tFILTER (STRDT(str(?o), xsd:integer) {}  {})""".format(
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
        hash_code = hash(research_uri + linkset_uri + c_filter)
        hash_code = str(hash_code).replace("-", "N") if str(hash_code).__contains__("-") else "P{}".format(hash_code)
        filter_uri = "{}c_filter_{}".format(Ns.risis, hash_code)

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
            research_uri, Ns.alivocab, filter_uri, Ns.riclass, linkset_uri, Ns.rdfs, c_filter, method)

    print query

    # REGISTER IT
    response = boolean_endpoint_response(query)

    print response
    # return query


def get_linkset_filter(research_uri, linkset_uri, filter_uri=''):

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
    """.format(research_uri, Ns.riclass, Ns.alivocab, linkset_uri, filter_uri)

    print query

    result = sparql_xml_to_matrix(query)

    return result

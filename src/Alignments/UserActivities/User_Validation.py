import src.Alignments.NameSpace as Ns
from src.Alignments.Query import boolean_endpoint_response

def updateEvidence(singleton_uri, message, research_uri, accepted=True):
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

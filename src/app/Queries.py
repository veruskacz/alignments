PREFIX ="""
    PREFIX bdb: <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset: <http://risis.eu/linkset/>
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX alivocab: <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph: <http://risis.eu/alignment/temp-match/>
"""
def get_target_datasets(singleton_matrix):

    sample = """
            ### LINKSET WHERE A CORRESPONDENCE MIGHT HAV HAPPENED
            graph ?g
            {
                ?sub <_#_> ?obj .
            }"""

    union = "{"
    if len(singleton_matrix) > 2:
        for i in range(1, len(singleton_matrix)):
            if i == 1:
                union += sample.replace('_#_', singleton_matrix[i][0])
            else:
                union += "\n\t     }\n\t      UNION\n\t     {" + sample.replace('_#_', singleton_matrix[i][0])
            if i == len(singleton_matrix)-1:
                union += "\n\t     }"
    else:
        union = """
        graph ?g
        {{
            ?sub <{}> ?obj .
        }}""".format(singleton_matrix[1][0])

    query = """
    {}
    select distinct ?graph ?subjectsTarget ?objectsTarget ?alignsSubjects ?alignsObjects ?alignsMechanism
    where
    {{
        ### Initially, we have A -> B via Z
        ### Z is derived from X, Y and W
        ### So we could replaced Z with X or Y or Z and find out the graph for with the assertion holds
        {}

        ### Once we find those graphs, it means that we can extract the same source
        ### and target datasets that hold details about the entities being linked
        ?graph
           void:subjectsTarget 			?subjectsTarget ;
           void:objectsTarget  			?objectsTarget .
        OPTIONAL {{ ?graph	  alivocab:alignsMechanism  ?alignsMechanism }}
        OPTIONAL {{ ?graph    alivocab:alignsSubjects   ?alignsSubjects }}
        OPTIONAL {{ ?graph    alivocab:alignsObjects    ?alignsObjS }}

        ### Here, we could easily have the description of the entities from
        ### the source and target datasets
        ### and... VOILA!!!
        ### The only thing is that all ?graph being linksets :(
        ### More to come on the mixed :-)
        graph ?source
        {{
           ?sub ?srcPre ?srcObj.
        }}

        graph ?target
        {{
           ?obj ?trgPre ?trgObj.
        }}
        BIND (IF(bound(?alignsObjS), ?alignsObjS , "resource identifier") AS ?alignsObjects)
    }}
    """.format(PREFIX, union)

    # print query
    return query

def get_correspondences(graph_uri):
    query = PREFIX + """
        select distinct ?sub ?pred ?obj
        {
            GRAPH <""" + graph_uri + """>
            { ?sub ?pred ?obj }
            GRAPH ?g
            { ?pred ?p ?o }

        } limit 80
        """
    return query

def get_evidences(singleton, predicate=None):

    variable = ""
    pred = ""
    if predicate is None:
        variable = "?pred"
        pred = "?pred"
    else:
        pred = predicate

    query = """
    Select distinct ?obj {}
    {{
       GRAPH ?graph
  	   {{
            <{}> {} ?obj
       }}
    }}
    """.format(variable, singleton, pred)
    return query

# dict = {"1":"alivocab:exactStrSim1_aaea1f82-c0a3-4e6d-b653-ff8bd1e9406d",
#         "2": "linkset:subset_grid_orgref_C1_unknown_738f0f6f-34db-45a3-9be6-9405a16eb8f2"}
#
# get_target_datasets(["alivocab:exactStrSim1_aaea1f82-c0a3-4e6d-b653-ff8bd1e9406d",
#                      "linkset:subset_grid_orgref_C1_unknown_738f0f6f-34db-45a3-9be6-9405a16eb8f2",
#                      "linkset:subset_orgref_grid_C1_unknown_64a0785b-4811-4f39-ae90-58587740cd23"])


PREFIX ="""
    PREFIX bdb:         <http://vocabularies.bridgedb.org/ops#>
    PREFIX rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX linkset:     <http://risis.eu/linkset/>
    PREFIX void:        <http://rdfs.org/ns/void#>
    PREFIX alivocab:    <http://risis.eu/alignment/predicate/>
    PREFIX tmpgraph:    <http://risis.eu/alignment/temp-match/>
    PREFIX prov:        <http://www.w3.org/ns/prov#>
"""

INFO = False
DETAIL = True


def get_graph_type(graph):
    query = """
    SELECT *
    {{
        <{}> a ?type .
    }}
    """.format(graph)
    if DETAIL:
        print query
    return query

def get_entity_type(graph):
    query = """
    SELECT distinct ?uri
    {{
        GRAPH <{}> {{
        ?s a ?uri
        }}
    }}
    """.format(graph)
    if DETAIL:
        print query
    return query


def get_graph_lens():
    query = PREFIX + """
    ### GET THE LENSES
    SELECT DISTINCT ?g ?triples ?operator
    WHERE
    {
        ?g
            rdf:type	        bdb:Lens ;
            alivocab:operator   ?operator ;
            void:triples        ?triples .
    }
    """
    if DETAIL:
        print query
    return query


def get_graph_linkset():
    query = PREFIX + """
    ### GET LINKSET GRAPHS
    SELECT DISTINCT ?g ?g_label ?subjectTargetURI ?subjectTarget
                    ?objectTargetURI ?objectTarget ?triples
                    ?alignsSubjects ?alignsObjects ?alignsMechanism
    WHERE
    {
        ?g
            rdf:type	                                            void:Linkset ;
            <http://rdfs.org/ns/void#subjectsTarget>                ?subjectTargetURI ;
            <http://rdfs.org/ns/void#objectsTarget>                 ?objectTargetURI ;
            <http://rdfs.org/ns/void#triples>                       ?triples ;
            <http://risis.eu/alignment/predicate/alignsSubjects>    ?alignsSubjects ;
            <http://risis.eu/alignment/predicate/alignsObjects>     ?alignsObjects ;
            <http://risis.eu/alignment/predicate/alignsMechanism>   ?alignsMechanism .

        #FILTER regex(str(?g), 'linkset', 'i')
        BIND(strafter(str(?g),'linkset/') AS ?g_label)
        BIND(UCASE(strafter(str(?subjectTargetURI),'dataset/')) AS ?subjectTarget)
        BIND(UCASE(strafter(str(?objectTargetURI),'dataset/')) AS ?objectTarget)
    }
    """
    if DETAIL:
        print query
    return query


def get_linkset_metadata(linkset):
    query = PREFIX + """
    ### GET LINKSET METADATA
    SELECT DISTINCT ?subjectTarget ?objectTarget ?triples
                    ?alignsSubjects ?alignsObjects ?alignsMechanism
    WHERE
    {{
        <{}>
            rdf:type	                                            void:Linkset ;
            <http://rdfs.org/ns/void#subjectsTarget>                ?subjectTarget ;
            <http://rdfs.org/ns/void#objectsTarget>                 ?objectTarget ;
            <http://rdfs.org/ns/void#triples>                       ?triples ;
            <http://risis.eu/alignment/predicate/alignsSubjects>    ?alignsSubjects ;
            <http://risis.eu/alignment/predicate/alignsObjects>     ?alignsObjects ;
            <http://risis.eu/alignment/predicate/alignsMechanism>   ?alignsMechanism .
    }}
    """.format(linkset)
    if DETAIL:
        print query
    return query

## Ve test
def get_targets(graph_uri):
    query = PREFIX + """
    ### GET LINKSET METADATA
    SELECT DISTINCT ?g
    WHERE
    {
            { <""" + graph_uri + """> <http://rdfs.org/ns/void#subjectsTarget>                ?g }
            UNION
            { <""" + graph_uri + """> <http://rdfs.org/ns/void#objectsTarget>                 ?g }
            UNION
            { <""" + graph_uri + """> void:target                                             ?g }
    }
    """
    if DETAIL:
        print query
    return query

def get_lens_operator(lens):
    query = PREFIX + """
    SELECT *
    {{
        <{}> alivocab:operator ?operator .
    }}
    """.format(lens)
    if DETAIL:
        print query
    return query


def get_lens_union_targets(lens):
    query = PREFIX + """
    select *
    {{
        <{}> void:target ?target .
    }}
    """.format(lens)
    if DETAIL:
        print query
    return query


def get_graphs_per_type(type=None):

    if type == "dataset":
        type_filter = "FILTER NOT EXISTS { {?uri   rdf:type	void:Linkset} "
        type_filter += " UNION {?uri   rdf:type	bdb:Lens} "
        type_filter += " UNION {?uri   rdf:type	void:View} } ."
    elif type == "linkset&lens":
        type_filter = " { ?uri   rdf:type	void:Linkset } UNION"
        type_filter += " { ?uri   rdf:type	void:Lens } ."
    elif type == "linkset":
        type_filter = "?uri   rdf:type	void:Linkset ."
    elif type == "lens":
        type_filter = "?uri   rdf:type	bdb:Lens ."
    elif type == "view":
        type_filter = "?uri   rdf:type	void:View ."
    else:
        type_filter = ""

    query = PREFIX + """
    ### GET DISTINCT GRAPHS
    SELECT DISTINCT ?uri
    WHERE
    {{
        GRAPH ?uri
        {{
            ?s ?p ?o
        }}
        {}
    }}
    """.format(type_filter)
    if DETAIL:
        print query
    return query


def get_correspondences(graph_uri):

    query = """
    ### GET CORRESPONDENCES
    SELECT DISTINCT ?sub ?pred ?obj
    {
        GRAPH <""" + graph_uri + """> { ?sub ?pred ?obj }
        GRAPH ?g { ?pred ?p ?o }

    } limit 80
    """
    if DETAIL:
        print query
    return query


def get_target_datasets(singleton_matrix):

    sample = """
    ### LINKSET WHERE A CORRESPONDENCE MIGHT HAVE HAPPENED
    GRAPH ?graph { ?sub <_#_> ?obj .
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
        GRAPH ?graph
        {{
            ?sub <{}> ?obj .
        }}""".format(singleton_matrix[1][0])

    query = """
    ### GET TARGET DATASETS
    ### THIS FUNCTION EXTRACTS THE TARGET DATASETS INVOLVED IN THE CREATION OF A CORRESPONDENCE
    {}
    SELECT DISTINCT ?sub ?obj ?graph ?subjectsTarget ?objectsTarget ?alignsSubjects ?alignsObjects ?alignsMechanism
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

        # ### Here, we could easily have the description of the entities from
        # ### the source and target datasets
        # ### and... VOILA!!!
        # ### The only thing is that all ?graph being linksets :(
        # ### More to come on the mixed :-)
        # GRAPH ?source
        # {{
        #    ?sub ?srcPre ?srcObj.
        # }}
        #
        # GRAPH ?target
        # {{
        #    ?obj ?trgPre ?trgObj.
        # }}
        BIND (IF(bound(?alignsObjS), ?alignsObjS , "resource identifier") AS ?alignsObjects)
    }}
    """.format(PREFIX, union)

    if DETAIL:
        print query
    return query


def get_evidences(singleton, predicate=None):

    variable = ""
    pred = ""
    if predicate is None:
        variable = "?pred"
        pred = "?pred"
    else:
        pred = predicate

    query = PREFIX + """
    ### GET EVIDENCES FOR SINGLETON
    SELECT DISTINCT ?obj {0}
    {{
        {{
           GRAPH ?graph
           {{
                <{1}> {2} ?obj .
           }}
        }}
        UNION
        {{
            GRAPH ?graph
            {{
                <{1}> ?pred2 ?obj_2 .
                ?obj_2 {2} ?obj .
                #graph ?g {{ ?obj_2 {2} ?obj }}.
            }}
        }}
    }}
    """.format(variable, singleton, pred)
    if DETAIL:
        print query
    return query


def get_resource_description(graph, resource, predicate=None):

    triples = ""

    if predicate is None:
        triples = "\n\t   <{}> ?pred ?obj .".format(resource)

    elif type(predicate) is list:
        for i in range(len(predicate)):
            if predicate[i] != "resource identifier":
                triples += "\n\t   <{}> <{}> ?obj_{} .".format(resource, predicate[i], i)
        # print "TRIPLES", triples

    elif type(predicate) is str:
        if predicate != "resource identifier":
            triples += "\n\t   <{}> <{}> ?obj .".format(resource, predicate)

    query = """
    ### GET RESOURCE DESCRIPTION
    SELECT DISTINCT *
    {{
        GRAPH <{}>
        {{{}
        }}
    }}
    """.format(graph, triples)
    if DETAIL:
        print query
    return query


def get_predicates(graph):

    query = """
    ### GET PREDICATES WITHIN A CERTAIN GRAPH
    SELECT ?pred (MAX(?o) AS ?obj)
    {
        GRAPH <""" + graph + """>
        {
            ?s ?pred ?o
        }
        FILTER (lcase(str(?o)) != 'null')
    } GROUP BY ?pred
    """
    if DETAIL:
        print query
    return query


def get_aligned_predicate_value(source, target, src_aligns, trg_aligns):

    query = """
    ### GET VALUES OF ALIGNED PREDICATES
    SELECT DISTINCT ?srcPredValue ?trgPredVal
    {
        GRAPH ?g_source
        {
            <""" + source + """>
                <""" + src_aligns + """>        ?srcPredValue
        }
        OPTIONAL
        {
            graph ?g_target
            {
                <""" + target + """>
                    <""" + trg_aligns + """>    ?trgPredVal
            }
        }
        FILTER((?g_source) != (?g_target))
        BIND (IF(bound(?trgPredVal), ?trgPredVal , "") AS ?trgPredValue)
    }
    """
    if DETAIL:
        print query
    return query

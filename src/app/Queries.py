import src.Alignments.NameSpace as Ns

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

def delete_rq():
    query = """
    DELETE {  ?subject ?pred ??obj . }
    WHERE
    {
        ?subject    a           <http://risis.eu/class/ResearchQuestion> ;
                    ?pred      ?obj .
    }
    """
    if DETAIL:
        print query
    return query


def associate_linkset_lens_to_rq(question_uri, linkset):

    query = """
    INSERT
    {{
        <{0}> alivocab:created <{1}>
    }}
    WHERE
    {{
        <{0}> ?pred ?obj .
    }}
    """.format(question_uri, linkset)
    if DETAIL:
        print query
    return query


def insert_ds_mapping(question_uri, mapping):
    # print "\nEnter the function"
    where_clause = ""
    insert_clause = ""
    insert_query = ""
    count_ds = 0
    for dataset, datatypes in mapping.items():
        # NEW MAPPING INSTANCE
        outer_colon = ";\n" if (count_ds > 0) else ""
        count_ds += 1
        where_clause = """
    \tBIND(iri(replace('http://risis.eu/activity/idea_#','#',strafter(str(uuid()),'uuid:'))) as ?dataset_{})\n""".\
            format(count_ds)

        insert_clause = """
        <{}> void:target ?dataset_{}.""".format(question_uri, count_ds)
        for i in range(len(datatypes)):
            insert_clause += """
        ?dataset_{}
            alivocab:selectedSource 	<{}> ;
            alivocab:selectedDatatype 	<{}> .\n""".format(count_ds, dataset, datatypes[i])

            colon = ";\n" if (i > 0) else ""
            insert_query += outer_colon + """
            {}INSERT
            {{
                {}
            }}
            WHERE
            {{
                {}
                FILTER NOT EXISTS
                {{
                     <{}> void:target [
                        alivocab:selectedSource     <{}> ;
                        alivocab:selectedDatatype   <{}>]
                }}
            }}
            """.format(colon, insert_clause, where_clause, question_uri, dataset, datatypes[i])

    final_query = PREFIX + insert_query


    if DETAIL:
        print final_query
    return final_query


def insert_RQ( question ):

    query = """
    ### CREATING A RESEARCH QUESTION RESOURCE
    INSERT
	{{
      	?subject
      	    a               <http://risis.eu/class/ResearchQuestion> ;
        	rdfs:label      ""\"{}\""" .
    }}
    WHERE
    {{
        #replace('http://risis.eu/activity/#','#', strafter(str(uuid()),'uuid:'))
        BIND( iri(replace('http://risis.eu/activity/idea_#','#', strafter(str(uuid()),'uuid:'))) as ?subject)
    }}
    """.format(question)

    if DETAIL:
        print query
    return query


def check_RQ_existance (question):
    query = """
    ask
	{{
      	?subject a <http://risis.eu/class/ResearchQuestion> ;
        	rdfs:label ""\"{}\""".
    }}""".format(question)
    if DETAIL:
        print query
    return query


def get_source_per_rq(rq_uri):
    query = PREFIX + """
    ### GET SOURCE PER RESEARCH QUESTION
    SELECT DISTINCT ?uri ?mode
    {{
        GRAPH <{0}>
        {{
            <{0}>
                a                    <http://risis.eu/class/ResearchQuestion> ;
                alivocab:selected    ?uri .
            BIND("no-mode" as ?mode)
        }}
    }}""".format(rq_uri)
    if DETAIL:
        print query
    return query


def get_rqs ():
    query = """
    SELECT DISTINCT ?uri ?uri_label
	{{
	    GRAPH ?uri
	    {{
      	    ?uri a <http://risis.eu/class/ResearchQuestion> ;
      	        rdfs:label ?uri_label .
      	}}
    }}"""
    if DETAIL:
        print query
    return query

# TODO: remove
def find_rq (question):
    query = """
    SELECT ?rq
	{{
      	?rq a <http://risis.eu/class/ResearchQuestion> ;
        	rdfs:label ""\"{}\""".
    }}""".format(question)
    if DETAIL:
        print query
    return query


def get_types_per_graph(rq_uri, mode):
    # print rq_uri, mode
    filter = """
        GRAPH <{0}>
          {{  <{0}> alivocab:selected ?Dataset
          }}
        """.format(rq_uri)
    if (mode == 'toAdd'):
        filter = 'FILTER NOT EXISTS {' + filter + '}'

    # print filter

    query = PREFIX + """
    select distinct ?Dataset ?EntityType (count(distinct ?x) as ?EntityCount)
    {{
        {0}

        Graph ?Dataset
        {{
           ?x a ?EntityType .

           FILTER NOT EXISTS {{ ?Dataset a <http://risis.eu/class/ResearchQuestion> }}
        }}
        FILTER ((str(?EntityType) != "http://www.w3.org/2000/01/rdf-schema#Class") )
        FILTER ((str(?EntityType) != "http://www.w3.org/2002/07/owl#Class"))
        FILTER ((str(?EntityType) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"))
        FILTER ((str(?EntityType) != "http://risis.eu/risis/ontology/class/Neutral"))

    }} GROUP by ?Dataset ?EntityType ORDER BY ?Dataset
    """.format(filter)

    if DETAIL:
        print query
    return query


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


# def get_entity_type(graph):
#     query = """
#     SELECT distinct ?uri
#     {{
#         GRAPH <{}> {{
#         ?s a ?uri
#         }}
#     }}
#     """.format(graph)
#     if DETAIL:
#         print query
#     return query


def get_entity_type_rq(rq_uri, graph_uri):
    query = PREFIX + """
    ### GET ENTITYTYPE PER DATASET IN THE SCOPE OF THE RESEARCH QUESTION
    SELECT DISTINCT ?uri
    {{
    	GRAPH <{0}>
	    {{
          	<{0}> a <http://risis.eu/class/ResearchQuestion> ;
          	     alivocab:selected  <{1}> .

          	<{1}>
          	    alivocab:hasDatatype  ?uri .
        }}
    }}""".format(rq_uri, graph_uri)
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


# def get_graphs_per_type(type=None):
#
#     if type == "dataset":
#         type_filter = "FILTER NOT EXISTS { {?uri   rdf:type	void:Linkset} "
#         type_filter += " UNION {?uri   rdf:type	bdb:Lens} "
#         type_filter += " UNION {?uri   rdf:type	void:View} } ."
#     elif type == "linkset&lens":
#         type_filter = " { ?uri   rdf:type	void:Linkset } UNION"
#         type_filter += " { ?uri   rdf:type	bdb:Lens } ."
#     elif type == "linkset":
#         type_filter = "?uri   rdf:type	void:Linkset ."
#     elif type == "lens":
#         type_filter = "?uri   rdf:type	bdb:Lens ."
#     elif type == "view":
#         type_filter = "?uri   rdf:type	void:View ."
#     else:
#         type_filter = ""
#
#     query = PREFIX + """
#     ### GET DISTINCT GRAPHS
#     SELECT DISTINCT ?uri ("null" as ?mode)
#     WHERE
#     {{
#         GRAPH ?uri
#         {{
#             ?s ?p ?o
#         }}
#         {}
#     }}
#     """.format(type_filter)
#     if DETAIL:
#         print query
#     return query


def get_graphs_per_rq_type(rq_uri, type=None):
    if type == "dataset":
        type_filter = """
        FILTER NOT EXISTS { {?uri   rdf:type	void:Linkset}
        UNION {?uri   rdf:type	bdb:Lens}
        UNION {?uri   rdf:type	void:View}
        } ."""
    elif type == "linkset&lens":
        type_filter = """
        { ?uri   rdf:type	void:Linkset } UNION
        { ?uri   rdf:type	void:Lens } . """
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
    SELECT DISTINCT ?uri ?mode
    WHERE
    {{
        GRAPH <{0}>
        {{
            ### SELECTING THE DATASETS
            <{0}> a <http://risis.eu/class/ResearchQuestion> .
            {{
                <{0}>  alivocab:selected    ?uri .
                BIND("no-mode" as ?mode)
            }}

            UNION

            ### SELECTING CREATED LENS OR LINKSETS
            {{
                <{0}>  alivocab:created*/alivocab:created  ?uri .
                BIND("success" as ?mode)
            }}

            UNION

            ### SELECTING USED LENS OR LINKSETS
            {{
                <{0}>  alivocab:created*/prov:used  ?uri.
                BIND("info" as ?mode)
            }}
        }}

        ### FILTER THE TYPE OF GRAPH
        {1}
    }}
    """.format(rq_uri, type_filter)
    if DETAIL:
        print query
    return query


def get_graphs_related_to_rq_type(rq_uri, type=None):
    if type == "linkset&lens":
        type_filter = """
        # THAT ARE OF TYPE LINKSET OR LENS
        { ?uri  rdf:type	void:Linkset }
        UNION
        { ?uri   rdf:type	 void:Lens } """
    elif type == "linkset":
        type_filter = """
        # THAT ARE OF TYPE LINKSET
        ?uri  rdf:type	void:Linkset """
    elif type == "lens":
        type_filter = """
        # THAT ARE OF TYPE LENS '
        ?uri   rdf:type	 bdb:Lens .
        """
    elif type == "view":
        type_filter = "?uri   rdf:type	 void:View ."
    else:
        type_filter = ""

    type_condition = """
    # WHICH ARE NOT A LINKSET WHOSE TARGET DATASETS (SOURCE OR OBJECT)
    # OR ARE NOT A LENS THAT TARGETS A LINKSET (THROUGH ZERO OR MORE LENSES) WHOSE TARGET DATASETS (SOURCE OR OBJECT)
    FILTER NOT EXISTS
    {{  ?uri  void:target*/(void:subjectsTarget|void:objectsTarget) ?dataset

        # ARE NOT WITHIN THE SELECTED DATASETS FOR A CERTAIN RESEARCH QUESTION
        FILTER NOT EXISTS
        {{
            GRAPH <{0}>
            {{
                <{0}>  alivocab:selected ?dataset  .
            }}
        }}
   	}} """.format(rq_uri)

    query = PREFIX + """
    ### GET DISTINCT GRAPHS
    SELECT DISTINCT ?uri ?mode
    WHERE
    {{

        # GRAPH-TYPE FILTER
        {0}

        # GRAPH-TYPE CONDITION
        {1}

        # AND WHICH ARE NOT ASSOCIATED TO THE RESEARCH QUESTION
        FILTER NOT EXISTS
        {{
            GRAPH <{2}>
            {{
                {{
                  <{2}>  alivocab:created*/alivocab:created   ?uri .
                }}
                UNION
                {{
                  <{2}>  alivocab:created*/prov:used  ?uri.
                }}
            }}
        }}

      BIND("no-mode" as ?mode)
    }}
    """.format(type_filter, type_condition, rq_uri)
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


def get_linkset_corresp_details(linkset, limit=1):

    query = PREFIX + """
    ### LINKSET DETAILS AND VALUES OF ALIGNED PREDICATES

    SELECT DISTINCT ?mechanism ?subTarget ?s_datatype ?s_property  ?objTarget ?o_datatype ?o_property ?s_PredValue ?o_PredValue ?triples ?operator
        WHERE
        {{

    	  <{0}>
          			 alivocab:alignsMechanism	 ?mechanism ;
     				 void:subjectsTarget	 	?subTarget ;
    				 bdb:subjectsDatatype	 	?s_datatype ;
     				 alivocab:alignsSubjects	 ?s_property;
     				 void:objectsTarget	 		?objTarget ;
    				 bdb:objectsDatatype	 	?o_datatype ;
     				 alivocab:alignsObjects	 	?o_property ;
                     void:triples                ?triples .


            GRAPH  <{0}>
            {{
                ?sub_uri    ?aligns        ?obj_uri
            }}.

            GRAPH ?subTarget
            {{
                ?sub_uri 	?s_property        ?s_PredValue
            }}
            OPTIONAL
            {{
                graph ?objTarget
                {{
                    ?obj_uri  ?o_property   ?o_PredVal
                }}
            }}
            BIND (IF(bound(?o_PredVal), ?o_PredVal , "none") AS ?o_PredValue)
            BIND ("" AS ?operator)
        }}
    LIMIT {1}
    """.format(linkset, limit)
    if DETAIL:
        print query
    return query


# TODO: ADD EXAMPLE VALUES
# TODO: MAKE GENERIC FOR BOH LENS AND LINKSET
def get_lens_corresp_details(lens, limit=1):

    query = PREFIX + """
    ### LENS DETAILS AND VALUES OF ALIGNED PREDICATES

    SELECT DISTINCT ?mechanism ?subTarget ?s_datatype ?s_property  ?objTarget ?o_datatype ?o_property ?s_PredValue ?o_PredValue ?triples ?operator
        WHERE
        {{

    	  <{0}>
          			 void:target* ?x .
          ?x

                                 void:subjectsTarget            ?subTarget ;
                                 bdb:subjectsDatatype           ?s_datatype ;
                                 alivocab:alignsSubjects        ?s_property;
                                 void:objectsTarget             ?objTarget ;
                                 bdb:objectsDatatype            ?o_datatype ;
                                 alivocab:alignsObjects         ?o_property .

    	  <{0}>
                     			 void:triples                   ?triples .


            OPTIONAL {{  <{0}>
                                 alivocab:alignsMechanism        ?mec ;}}
            OPTIONAL {{  <{0}>
                                 alivocab:operator   ?op  ;}}

            BIND (IF(bound(?mec), ?mec , "") AS ?mechanism)
            BIND (IF(bound(?op), ?op , "") AS ?operator)        }}
    LIMIT {1}
    """.format(lens, limit)
    if DETAIL:
        print query
    return query

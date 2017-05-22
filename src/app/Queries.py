# import sys
# sys.path.append('/Users/veruskacz/PyWebApp/alignments/src')
# sys.path.append('/Users/veruskacz/PyWebApp/alignments/src/Alignments')
# sys.path.append('/Users/veruskacz/PyWebApp/alignments/src/app')

import Alignments.NameSpace as Ns
from Alignments.UserActivities.User_Validation import get_linkset_filter

PREFIX ="""
    ################################################################
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

# def delete_rq():
#     query = """
#     DELETE {  ?subject ?pred ??obj . }
#     WHERE
#     {
#         ?subject    a           <http://risis.eu/class/ResearchQuestion> ;
#                     ?pred      ?obj .
#     }
#     """
#     if DETAIL:
#         print query
#     return query


# def associate_linkset_lens_to_rq(question_uri, linkset):
#
#     query = """
#     INSERT
#     {{
#         <{0}> alivocab:created <{1}>
#     }}
#     WHERE
#     {{
#         <{0}> ?pred ?obj .
#     }}
#     """.format(question_uri, linkset)
#     if DETAIL:
#         print query
#     return query


# def insert_ds_mapping(question_uri, mapping):
#     # print "\nEnter the function"
#     where_clause = ""
#     insert_clause = ""
#     insert_query = ""
#     count_ds = 0
#     for dataset, datatypes in mapping.items():
#         # NEW MAPPING INSTANCE
#         outer_colon = ";\n" if (count_ds > 0) else ""
#         count_ds += 1
#         where_clause = """
#     \tBIND(iri(replace('http://risis.eu/activity/idea_#','#',strafter(str(uuid()),'uuid:'))) as ?dataset_{})\n""".\
#             format(count_ds)
#
#         insert_clause = """
#         <{}> void:target ?dataset_{}.""".format(question_uri, count_ds)
#         for i in range(len(datatypes)):
#             insert_clause += """
#         ?dataset_{}
#             alivocab:selectedSource 	<{}> ;
#             alivocab:selectedDatatype 	<{}> .\n""".format(count_ds, dataset, datatypes[i])
#
#             colon = ";\n" if (i > 0) else ""
#             insert_query += outer_colon + """
#             {}INSERT
#             {{
#                 {}
#             }}
#             WHERE
#             {{
#                 {}
#                 FILTER NOT EXISTS
#                 {{
#                      <{}> void:target [
#                         alivocab:selectedSource     <{}> ;
#                         alivocab:selectedDatatype   <{}>]
#                 }}
#             }}
#             """.format(colon, insert_clause, where_clause, question_uri, dataset, datatypes[i])
#
#     final_query = PREFIX + insert_query
#
#
#     if DETAIL:
#         print final_query
#     return final_query


# def insert_RQ( question ):
#
#     query = """
#     ### CREATING A RESEARCH QUESTION RESOURCE
#     INSERT
# 	{{
#       	?subject
#       	    a               <http://risis.eu/class/ResearchQuestion> ;
#         	rdfs:label      ""\"{}\""" .
#     }}
#     WHERE
#     {{
#         #replace('http://risis.eu/activity/#','#', strafter(str(uuid()),'uuid:'))
#         BIND( iri(replace('http://risis.eu/activity/idea_#','#', strafter(str(uuid()),'uuid:'))) as ?subject)
#     }}
#     """.format(question)
#
#     if DETAIL:
#         print query
#     return query


# def check_RQ_existance (question):
#     query = """
#     ask
# 	{{
#       	?subject a <http://risis.eu/class/ResearchQuestion> ;
#         	rdfs:label ""\"{}\""".
#     }}""".format(question)
#     if DETAIL:
#         print query
#     return query


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
    {
        GRAPH ?uri
        {
            ?uri
                a           <http://risis.eu/class/ResearchQuestion> ;
                rdfs:label  ?uri_label .
        }
    }"""
    if DETAIL:
        print query
    return query

# def find_rq (question):
#     query = """
#     SELECT ?rq
# 	{{
#       	?rq a <http://risis.eu/class/ResearchQuestion> ;
#         	rdfs:label ""\"{}\""".
#     }}""".format(question)
#     if DETAIL:
#         print query
#     return query


def get_types_per_graph(rq_uri, mode):
    # print rq_uri, mode
    filter = """
        ## CHECK FOR DATASETS/GRAPHS SELECTED IN A RESERACH QUESTION
        GRAPH <{0}>
          {{  <{0}> alivocab:selected ?Dataset
          }}
        """.format(rq_uri)
    if (mode == 'toAdd'):
        filter = 'FILTER NOT EXISTS {' + filter + '}'

    # print filter

    query = PREFIX + """
    ## SELECT THE DATASETS/GRAPHS, ENTITY TYPE AND NUMBER OR ENTITYS OF THAT TYPE
    select distinct ?Dataset ?EntityType (count(distinct ?x) as ?EntityCount)
    {{
        {0}

        ### THE DATASETS/GRAPHS MUST NOT BE A RESERARCH QUESTION
        Graph ?Dataset
        {{
           ?x a ?EntityType .

           FILTER NOT EXISTS {{ ?Dataset a <http://risis.eu/class/ResearchQuestion> }}
        }}
        ### AND THE ENTITY-TYPES DESCRIBED MUST NOT BE ONE OF THE STANDARD VOCABULARIES
        FILTER ((str(?EntityType) != "http://www.w3.org/2000/01/rdf-schema#Class") )
        FILTER ((str(?EntityType) != "http://www.w3.org/2002/07/owl#Class"))
        FILTER ((str(?EntityType) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"))
        FILTER ((str(?EntityType) != "http://risis.eu/risis/ontology/class/Neutral"))

    }} GROUP by ?Dataset ?EntityType ORDER BY ?Dataset
    """.format(filter)

    if DETAIL:
        print query
    return query


# def get_graph_type(graph):
#     query = """
#     SELECT *
#     {{
#         <{}> a ?type .
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


def get_graph_lens(lens=''):
    filter = "FILTER (?g = <{}>)".format(lens) if lens else ''
    query = PREFIX + """
    ### GET THE LENSES
    SELECT DISTINCT ?g ?triples ?operator
    WHERE
    {{
        ?g
            rdf:type	        bdb:Lens ;
            alivocab:operator   ?operator ;
            void:triples        ?triples .
        {}
    }}
    """.format(filter)
    if DETAIL:
        print query
    return query


def get_lens_specs(lens):
    filter = "FILTER (?g = <{}>)".format(lens) if lens else ''
    query = PREFIX + """
    ### GET THE LENSES
    SELECT DISTINCT ?g ?triples ?operator ?graph
    WHERE
    {{
        ?g
            rdf:type	        bdb:Lens ;
            alivocab:operator   ?operator ;
            void:triples        ?triples ;
            (void:target|void:subjectsTarget|void:objectsTarget)			?graph .
        {}
    }}
    """.format(filter)
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


# def get_linkset_metadata(linkset):
#     query = PREFIX + """
#     ### GET LINKSET METADATA
#     SELECT DISTINCT ?subjectTarget ?objectTarget ?triples
#                     ?alignsSubjects ?alignsObjects ?alignsMechanism
#     WHERE
#     {{
#         <{}>
#             rdf:type	                                            void:Linkset ;
#             <http://rdfs.org/ns/void#subjectsTarget>                ?subjectTarget ;
#             <http://rdfs.org/ns/void#objectsTarget>                 ?objectTarget ;
#             <http://rdfs.org/ns/void#triples>                       ?triples ;
#             <http://risis.eu/alignment/predicate/alignsSubjects>    ?alignsSubjects ;
#             <http://risis.eu/alignment/predicate/alignsObjects>     ?alignsObjects ;
#             <http://risis.eu/alignment/predicate/alignsMechanism>   ?alignsMechanism .
#     }}
#     """.format(linkset)
#     if DETAIL:
#         print query
#     return query


## Ve test
# def get_targets(graph_uri):
#     query = PREFIX + """
#     ### GET LINKSET METADATA
#     SELECT DISTINCT ?g
#     WHERE
#     {
#             { <""" + graph_uri + """> <http://rdfs.org/ns/void#subjectsTarget>                ?g }
#             UNION
#             { <""" + graph_uri + """> <http://rdfs.org/ns/void#objectsTarget>                 ?g }
#             UNION
#             { <""" + graph_uri + """> void:target                                             ?g }
#     }
#     """
#     if DETAIL:
#         print query
#     return query


# def get_lens_operator(lens):
#     query = PREFIX + """
#     SELECT *
#     {{
#         <{}> alivocab:operator ?operator .
#     }}
#     """.format(lens)
#     if DETAIL:
#         print query
#     return query


# def get_lens_union_targets(lens):
#     query = PREFIX + """
#     select *
#     {{
#         <{}> void:target ?target .
#     }}
#     """.format(lens)
#     if DETAIL:
#         print query
#     return query


def get_graphs_per_rq_type(rq_uri, type=None):
    type_filter = ""
    type_filter_view = ""
    if type == "dataset":
        type_filter = """
        FILTER NOT EXISTS { {?uri   rdf:type	void:Linkset}
        UNION {?uri   rdf:type	bdb:Lens}
        UNION {?uri   rdf:type	void:View}
        UNION {?uri   rdf:type	<http://risis.eu/class/ResearchQuestion>}
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
        type_filter_view = "?uri   rdf:type	<http://risis.eu/class/View> ."

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
                <{0}>  alivocab:created+  ?uri .
                BIND("success" as ?mode)
            }}

            UNION

            ### SELECTING USED LENS OR LINKSETS
            {{
                <{0}>  alivocab:created*/prov:used  ?uri.
                BIND("info" as ?mode)
            }}
            {2}
        }}

        ### FILTER THE TYPE OF GRAPH
        {1}
    }}
    """.format(rq_uri, type_filter, type_filter_view)
    if DETAIL:
        print query
    return query


def get_datasets():
    query = PREFIX + """
    ### GET DISTINCT DATASETS
    SELECT DISTINCT ?uri ?mode
    WHERE
    {
  		?uri   rdf:type	 _:type
        GRAPH ?uri {_:s  ?p  _:o}

        ### FILTER THE TYPE OF GRAPH
        FILTER NOT EXISTS { {?uri   rdf:type	void:Linkset}
        UNION {?uri   rdf:type	bdb:Lens}
        UNION {?uri   rdf:type	void:View}
        UNION {?uri   rdf:type	<http://risis.eu/class/ResearchQuestion>}
        } 
        
      BIND("no-mode" as ?mode)
    }
    """
    if DETAIL:
        print query
    return query


def get_graphs_related_to_rq_type(rq_uri, type=None):

    if type == "linkset&lens":
        type_filter = """
        # THAT ARE OF TYPE LINKSET OR LENS
        { ?uri  rdf:type	void:Linkset }
        UNION
        { ?uri   rdf:type	 void:Lens }
         """
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


def get_correspondences(rq_uri, graph_uri, filter_uri='', filter_term='', limit=80):

    # ADD FILTER CONDITIONS
    filter_condition = ""
    filter_count = ""
    filter_count_aux = ""
    result = get_linkset_filter(rq_uri, graph_uri, filter_uri)
    print result
    if result["result"]:
        method = result["result"][1][1]
        if method == "threshold":
            filter_condition = result["result"][1][0]
            # somehow this HAVING is needed to avoid return with empty sub pred obj
            #filter_condition += "BIND(count(distinct ?pred) as ?strength)"
            #filter_count = 'HAVING (?strength > 0)'
        else:
            filter_count = " GROUP BY ?sub ?pred ?obj "
            filter_count += result["result"][1][0]
            if method == "accept":
                filter_count_aux = """
                OPTIONAL {{ ?pred <http://risis.eu/alignment/predicate/hasValidation> ?accept.
                            ?accept rdf:type <http://www.w3.org/ns/prov#Accept> .
                         }}"""
            # TODO: CHANGE RISIS PREDICATE TO RISIS CLASS FOR REJECT
            elif method == "reject":
                filter_count_aux = """
            	OPTIONAL {{?pred <http://risis.eu/alignment/predicate/hasValidation> ?reject.
                            ?reject rdf:type <http://risis.eu/alignment/predicate/Reject> .
                         }}"""

    # ADD FILTER TERM MATCH
    filter_term_match = ''
    if filter_term != '':
        filter_term_match = """
        
        ### GETTING THE LINKSET AND DERIVED LINKSETS WHEN REFINED
        <{0}>
                prov:wasDerivedFrom*        ?graph_uri .
                
        ### GET METADATA IN THE DEFAULT GRAPH
        ?graph_uri  void:subjectsTarget 			?subjectsTarget ;
               void:objectsTarget  			?objectsTarget ;
               alivocab:alignsSubjects      ?alignsSubjects ;
               alivocab:alignsObjects    ?alignsObjects .
        
        {{
        ## MATCH USING ALIGNED PROPERTY IN THE SUBJECT-DATASET
        GRAPH ?subjectsTarget
            {{
                ?sub    ?alignsSubjects     ?Svalue .
                (?Svalue ?score) <tag:stardog:api:property:textMatch> \"\"\"{1}\"\"\".
            }}
        }}
        UNION
        {{
        ## MATCH USING ALIGNED PROPERTY IN THE OBJECT-DATASET
        GRAPH ?objectsTarget
            {{
                ?obj    ?alignsObjects     ?Ovalue .
                (?Ovalue ?score) <tag:stardog:api:property:textMatch> \"\"\"{1}\"\"\".
            }}
        }}
        """.format(graph_uri, filter_term)

    query = PREFIX + """
    ### GET CORRESPONDENCES
    SELECT DISTINCT ?sub ?pred ?obj 
    {{
        GRAPH <{1}> {{ ?sub ?pred ?obj }}
        GRAPH ?g {{ ?pred ?p ?o .
            # ADDITIONAL PATTERNS TO ALLOW FOR FILTER COUNT
            {4}
        }}
                
        # FILTER BY CONDITION
        {2}
        
        # FILTER BY TERM MATCH
        {5}
        
    }} 
    # FILTER BY COUNT
    {3}
    limit {0}
    """.format(limit, graph_uri, filter_condition, filter_count, filter_count_aux, filter_term_match)
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


def get_evidences(graph_name, singleton, predicate=None):

    variable = ""
    pred = ""
    if predicate is None:
        variable = "?pred"
        pred = "?pred"
    else:
        pred = predicate

    query = PREFIX + """
    ### GET EVIDENCES FOR SINGLETON
    SELECT DISTINCT {0} ?obj 
    {{
        GRAPH ?graph
        {{
            <{1}>   <http://www.w3.org/ns/prov#wasDerivedFrom>*   ?x
        }}
        {{
           GRAPH <{3}>
           {{
                ?x {2} ?obj .
                MINUS 
                {{
                    ?x <http://risis.eu/alignment/predicate/hasValidation> ?obj
                }}
           }}
        }}
        UNION
        {{
            GRAPH <{3}>
            {{
                ?x <http://risis.eu/alignment/predicate/hasValidation> ?obj_2 .
                ?obj_2 rdf:type 	?type ;
                	   rdfs:comment ?comment .
              	BIND (concat((strafter(str(?type),"/prov#")),(strafter(str(?type),"predicate/"))) as ?strType)
                BIND (concat( ?strType, ': ', ?comment) as ?obj)
                BIND (<http://risis.eu/alignment/predicate/hasValidation> as ?pred)
            }}
        }}
    }}
    """.format(variable, singleton, pred, graph_name)
    if DETAIL:
        print query
    return query


def get_evidences_counters(singleton_uri):
    query = PREFIX + """
    Select distinct ?nGood ?nBad ?nStrength
    {
    	{
         Select (count(distinct ?accepted) AS ?nGood)
         {
          GRAPH ?graph
      	   { <""" + singleton_uri + """> alivocab:hasValidation ?accepted .
      	    ?accepted rdf:type prov:Accept
           }
         }
        }

    	{
         Select (count(distinct ?rejected) AS ?nBad)
         {
          GRAPH ?graph
      	   { <""" + singleton_uri + """> alivocab:hasValidation ?rejected .
      	    ?rejected rdf:type alivocab:Reject
           }
         }
        }

        {
         Select (count(?derivedFrom) AS ?nStrength)
         {
          GRAPH ?graph
      	   { <""" + singleton_uri + """> prov:wasDerivedFrom ?derivedFrom
           }
         }
        }
    }
    """
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
    ### GET PREDICATES WITHIN A CERTAIN GRAPH WITH EXAMPLE VALUE
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


def get_predicates_list(graph, exclude_rdf_type=False):

    filter = ''
    if exclude_rdf_type:
        filter = " FILTER (?uri != rdf:type) "

    query = """
    ### GET DISTINCT PREDICATES WITHIN A CERTAIN GRAPH
    SELECT distinct ?uri 
    {{
        GRAPH <{}>
        {{
            ?s ?uri ?o
        }}
        {}
    }} 
    """.format(graph, filter)
    if DETAIL:
        print query
    return query

def get_dataset_predicate_values(graph, predicate):

    query = """
    ### GET DISTINCT VALUES OF FOR A PREDICATE WITHIN A CERTAIN GRAPH
    SELECT distinct (?value as ?uri) #named uri just for reusing the html template 
    {{
        GRAPH <{}>
        {{
            ?s <{}> ?value
        }}
    }} 
    """.format(graph, predicate)
    if DETAIL:
        print query
    return query

def get_aligned_predicate_value(source, target, src_aligns, trg_aligns):

    query = """
    ### GET VALUES OF ALIGNED PREDICATES
    SELECT DISTINCT ?srcPredValue ?trgPredValue
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


def get_linkset_corresp_sample_details(linkset, limit=1):

    query = PREFIX + """
    ### LINKSET DETAILS WITH SAMPLE OF ALIGNED PREDICATES

    SELECT DISTINCT
    ?subTarget ?objTarget ?s_datatype ?o_datatype ?operator
    (GROUP_CONCAT(?s_PredV; SEPARATOR=" | ") as ?s_PredValue)
    (GROUP_CONCAT(?o_PredV; SEPARATOR=" | ") as ?o_PredValue)
    (GROUP_CONCAT(?s_prop; SEPARATOR="|") as ?s_property)
    (GROUP_CONCAT(?o_prop; SEPARATOR="|") as ?o_property)
    (GROUP_CONCAT(?mec; SEPARATOR="|") as ?mechanism)
    (GROUP_CONCAT(?trip; SEPARATOR="|") as ?triples)

    WHERE
    {{

        ### GETTING THE LINKSET AND DERIVED LINKSETS WHEN REFINED
        <{0}>
            prov:wasDerivedFrom*        ?linkset .

        ### RETRIEVING LINKSET METADATA
        ?linkset
            alivocab:alignsMechanism    ?mec ;
            void:subjectsTarget         ?subTarget ;
            bdb:subjectsDatatype        ?s_datatype ;
            alivocab:alignsSubjects     ?s_prop;
            void:objectsTarget          ?objTarget ;
            bdb:objectsDatatype         ?o_datatype ;
            alivocab:alignsObjects      ?o_prop ;
            void:triples                ?trip .

        ### RETRIEVING CORRESPONDENCES
        GRAPH  <{0}>
        {{
            ?sub_uri    ?aligns        ?obj_uri
        }}.

        ### RETRIEVING SUBJECT DATASET INFO
        GRAPH ?subTarget
        {{
            ?sub_uri    ?s_prop     ?s_PredV
        }}

        ### RETRIEVING OBJECT DATASET INFO WHEN EXISTS
        ### SOME ALIGNMENTS LIKE EMBEDDED SUBSET DO NOT USE OBJECT DATASET
        OPTIONAL
        {{
            graph ?objTarget
            {{
                ?obj_uri  ?o_prop   ?o_PredVal
            }}
        }}
        BIND (IF(bound(?o_PredVal), ?o_PredVal , "none") AS ?o_PredV)
        BIND ("" AS ?operator)
    }}
    group by ?subTarget ?objTarget  ?sub_uri ?obj_uri  ?s_datatype ?o_datatype ?operator
    LIMIT {1}""".format(linkset, limit)
    if DETAIL:
        print query
    return query


def get_linkset_corresp_details(linkset, limit=1):

    query = PREFIX + """
    ### LINKSET DETAILS

    SELECT DISTINCT ?mechanism ?subTarget ?s_datatype ?s_property
    ?objTarget ?o_datatype ?o_property  ?triples ?operator
        WHERE
        {{

            ### GETTING THE LINKSET AND DERIVED LINKSETS WHEN REFINED
            <{0}>
                prov:wasDerivedFrom*        ?linkset .

            ### RETRIEVING LINKSET METADATA
            ?linkset
                alivocab:alignsMechanism    ?mechanism ;
                void:subjectsTarget         ?subTarget ;
                bdb:subjectsDatatype        ?s_datatype ;
                alivocab:alignsSubjects     ?s_property;
                void:objectsTarget          ?objTarget ;
                bdb:objectsDatatype         ?o_datatype ;
                alivocab:alignsObjects      ?o_property ;
                void:triples                ?triples .

            BIND ("" AS ?operator)
        }}
    # LIMIT {1}
    """.format(linkset, limit)
    if DETAIL:
        print query
    return query


def get_lens_corresp_details(lens, limit=1):

    query = PREFIX + """
    ### LENS DETAILS AND VALUES OF ALIGNED PREDICATES

    SELECT DISTINCT ?mechanism ?subTarget ?s_datatype ?s_property
    ?objTarget ?o_datatype ?o_property ?s_PredValue ?o_PredValue ?triples ?operator
    WHERE
    {{

        <{0}>
             void:target+|void:subjectsTarget|void:objectsTarget ?x .
        ?x

            void:subjectsTarget            ?subTarget ;
            bdb:subjectsDatatype           ?s_datatype ;
            alivocab:alignsSubjects        ?s_property ;
            void:objectsTarget             ?objTarget ;
            bdb:objectsDatatype            ?o_datatype ;
            alivocab:alignsObjects         ?o_property .

        #<{0}>
        #    void:triples                   ?triples .

        {{
            select (count (?sub) as ?triples )
            where
            {{
                GRAPH <{0}>
                {{
                  ?sub ?sing ?obj .
                  ?sing ?pred ?sObj .
                }}
            }}
        }}


        OPTIONAL
        {{  <{0}>
            alivocab:alignsMechanism        ?mec .
        }}

        OPTIONAL
        {{  <{0}>
            alivocab:operator   ?op  .
        }}

        BIND (IF(bound(?mec), ?mec , "") AS ?mechanism)
        BIND (IF(bound(?op), ?op , "") AS ?operator)
    }}
    LIMIT {1}""".format(lens, limit)
    if DETAIL:
        print query
    return query


def get_filter(research_uri, graph_uri):

    query = """
    SELECT (?filter as ?id) (?filter as ?uri) ?description
    {{
        GRAPH <{0}>
        {{
            ?filter
                a <{1}Filter> ;
                <{2}appliesTo>  <{3}> ;
                rdfs:comment ?comment ;
                <{2}method>  ?method .
        }}
        BIND (CONCAT(UCASE(?method), " | ", ?comment) AS ?description)
    }}
    """.format(research_uri, Ns.riclass, Ns.alivocab, graph_uri)

    if DETAIL:
        print query

    return query

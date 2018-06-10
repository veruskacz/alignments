# import sys

import Alignments.NameSpace as Ns
import Alignments.Utility as Ut
from Alignments.Query import linkset_aligns_prop
from Alignments.Query import sparql_xml_to_matrix as sparql_matrix
from Alignments.UserActivities.User_Validation import get_graph_filter

PREFIX ="""
    ################################################################
    PREFIX bdb:         <{6}>
    PREFIX rdf:         <{5}>
    PREFIX linkset:     <{4}>
    PREFIX void:        <{3}>
    PREFIX alivocab:    <{0}>
    PREFIX tmpgraph:    <{2}>
    PREFIX prov:        <{1}>
    PREFIX skos:        <{7}>    
""".format(Ns.alivocab, Ns.prov, Ns.tmpgraph, Ns.void, Ns.linkset, Ns.rdf, Ns.bdb, Ns.skos)

INFO = False
DETAIL = True


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


def get_types_per_graph(rq_uri, mode):
    filter = """
        ## CHECK FOR DATASETS/GRAPHS SELECTED IN A RESERACH QUESTION
        GRAPH <{0}>
          {{  <{0}> alivocab:selected ?Dataset .

              ?Dataset alivocab:hasDatatype  ?EntityType .
          }}
        """.format(rq_uri)
    if (mode == 'toAdd'):
        filter = 'FILTER NOT EXISTS {' + filter + '}'

    query = PREFIX + """
    ## SELECT THE DATASETS/GRAPHS, ENTITY TYPE AND NUMBER OR ENTITYS OF THAT TYPE
    select distinct ?Dataset ?EntityType (count(distinct ?x) as ?EntityCount)
            (CONCAT( REPLACE(str(?Dataset), '^(.*[/])', '' )  , ' | ',
                     REPLACE(str(?EntityType), '^(.*[/])', '' )) as ?descr)
    {{
        {0}

        ### THE DATASETS/GRAPHS MUST NOT BE A RESERARCH QUESTION
        Graph ?Dataset
        {{
           ?x a ?EntityType .

           FILTER NOT EXISTS {{ ?Dataset a <http://risis.eu/class/ResearchQuestion> }}
        }}
        ### AND THE ENTITY-TYPES DESCRIBED MUST NOT BE ONE OF THE STANDARD VOCABULARIES
        FILTER (?EntityType != <http://www.w3.org/2000/01/rdf-schema#Class>)
        FILTER (?EntityType != <http://www.w3.org/2002/07/owl#Class>)
        FILTER (?EntityType != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>)
        FILTER (?EntityType != <http://risis.eu/risis/ontology/class/Neutral>)
        FILTER (?EntityType != <http://www.w3.org/ns/prov#Accept>)
        FILTER (?EntityType != <http://risis.eu/alignment/predicate/Reject>)

    }} GROUP by ?Dataset ?EntityType ORDER BY ?Dataset
    """.format(filter)

    if DETAIL:
        print query
    return query


def get_entity_type_rq(rq_uri, graph_uri):

    query_rq = ""
    print rq_uri, type(rq_uri)
    if rq_uri:
        query_rq = """
        GRAPH <{0}>
        {{
            <{0}> a <http://risis.eu/class/ResearchQuestion> ;
                 alivocab:selected  <{1}> .

            <{1}>
                alivocab:hasDatatype  ?uri .
        }}
        """.format(rq_uri, graph_uri)

    query = PREFIX + """
    ### GET ENTITYTYPE PER DATASET IN THE SCOPE OF THE RESEARCH QUESTION
    SELECT DISTINCT ?uri (COUNT(?s) AS ?count)
    {{
        {0}

        GRAPH <{1}>
        {{
           ?s a ?uri .
        }}
    }} GROUP BY ?uri """.format(query_rq, graph_uri)
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


def get_graphs_per_rq_type(rq_uri, type=None, dataset=None):
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
        { ?uri   rdf:type	bdb:Lens } . """
    elif type == "linksetBiD":
        type_filter = """?uri   rdf:type	void:Linkset .
        { 	 ?uri
                   alivocab:alignsSubjects ?s_prop ;
                   alivocab:alignsObjects ?o_prop .

            BIND('oneAligns' as ?lkst_type_)
            filter (isBlank(?s_prop) = "FALSE"^^xsd:boolean && isBlank(?o_prop) = "FALSE"^^xsd:boolean)
            filter not exists
            {
			?uri
                    prov:wasDerivedFrom*/void:target*/prov:wasDerivedFrom*       ?graph .

            ?graph
                   alivocab:alignsSubjects ?s_prop2 ;
                   alivocab:alignsObjects ?o_prop2 .
            filter (isBlank(?s_prop2) = "TRUE"^^xsd:boolean || isBlank(?o_prop2) = "TRUE"^^xsd:boolean)
            }
        }
        UNION
        { 	?uri
                   alivocab:alignsSubjects ?s_prop ;
                   alivocab:alignsObjects ?o_prop .

            BIND('multipleAligns' as ?lkst_type_)
            filter (isBlank(?s_prop) = "FALSE"^^xsd:boolean && isBlank(?o_prop) = "FALSE"^^xsd:boolean)

            ?uri
                    prov:wasDerivedFrom*/void:target*/prov:wasDerivedFrom*       ?graph .

            ?graph
                   alivocab:alignsSubjects ?s_prop2 ;
                   alivocab:alignsObjects ?o_prop2 .
            filter (isBlank(?s_prop2) = "TRUE"^^xsd:boolean || isBlank(?o_prop2) = "TRUE"^^xsd:boolean)

        }
        ### SELECTING CREATED LENS OR LINKSETS
        UNION
        {
             ?uri
                   alivocab:alignsSubjects ?s_prop ;
                   alivocab:alignsObjects ?o_prop .

            # ?s_prop ?x ?y .
            # ?o_prop ?z ?w .
            # filter (isBlank(?y) = "TRUE"^^xsd:boolean)
            # filter (isBlank(?w) = "TRUE"^^xsd:boolean)

            BIND("success" as ?mode)
            BIND('multipleAligns' as ?lkst_type_)
            filter (isBlank(?s_prop) = "TRUE"^^xsd:boolean || isBlank(?o_prop) = "TRUE"^^xsd:boolean)

        }
        """
    elif type == "linksetMultiD":
        type_filter = """?uri   rdf:type	void:Linkset .
                 ?uri
                       alivocab:hasAlignmentTarget  ?target  .

                 BIND('multidimensional' as ?lkst_type_)
        """
    elif type == "linkset":
        type_filter = "?uri   rdf:type	void:Linkset ."
    elif type == "lens":
        type_filter = "?uri   rdf:type	bdb:Lens ."
    elif type == "view":
        type_filter_view = "?uri   rdf:type	<http://risis.eu/class/View> ."

    if dataset is not None:
        filter_dataset = """
            {{ ?uri    void:subjectsTarget|void:objectsTarget   <{0}> . }}
            UNION {{
                ?uri                alivocab:hasAlignmentTarget ?alignmentTarget .
                ?alignmentTarget    alivocab:hasTarget          <{0}>  .
            }}
        """.format(dataset)
    else:
        filter_dataset = ""


    query = PREFIX + """
    ### GET DISTINCT GRAPHS
    SELECT DISTINCT ?uri ?mode ?label ?lkst_type
    WHERE
    {{

        ### FILTER THE TYPE OF GRAPH
        {1}
        BIND (IF(bound(?lkst_type_), ?lkst_type_ , "-") AS ?lkst_type)

        GRAPH <{0}>
        {{
            ### SELECTING THE DATASETS
            <{0}> a <http://risis.eu/class/ResearchQuestion> .
            {{
                <{0}>  alivocab:selected    ?uri .
                #BIND("no-mode" as ?mode)
            }}

            UNION

            ### SELECTING CREATED LENS OR LINKSETS
            {{
                <{0}>  alivocab:created+  ?uri .
                BIND("success" as ?mode2)
            }}

            UNION

            ### SELECTING USED LENS OR LINKSETS
            {{
                <{0}>  alivocab:created*/prov:used  ?uri.
                BIND("info" as ?mode3)
            }}
            {2}
            BIND( IF(BOUND(?mode3),?mode3, IF(BOUND(?mode2),?mode2, "no-mode")) AS ?mode)
            OPTIONAL {{?uri   skos:prefLabel		?label_ .}}
            BIND (IF(bound(?label_), ?label_ , "-") AS ?label)

        }}

        ### FILTER THE ALIGNED DATASET
        {3}
    }}
    """.format(rq_uri, type_filter, type_filter_view, filter_dataset)
    if DETAIL:
        print query
    return query


def get_datasets():
    query = PREFIX + """
    ### GET DISTINCT DATASETS
    SELECT DISTINCT ?uri ?mode
    WHERE
    {
        GRAPH ?uri {_:s  a  ?EntityType .
           FILTER NOT EXISTS { ?uri a <http://risis.eu/class/ResearchQuestion> }
        }

        ### AND THE ENTITY-TYPES DESCRIBED MUST NOT BE ONE OF THE STANDARD VOCABULARIES
        FILTER (?EntityType != <http://www.w3.org/2000/01/rdf-schema#Class>)
        FILTER (?EntityType != <http://www.w3.org/2002/07/owl#Class>)
        FILTER (?EntityType != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property>)
        FILTER (?EntityType != <http://risis.eu/risis/ontology/class/Neutral>)
        FILTER (?EntityType != <http://www.w3.org/ns/prov#Accept>)
        FILTER (?EntityType != <http://risis.eu/alignment/predicate/Reject>)

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
    elif type == "linksetBiD":
        type_filter = """?uri   rdf:type	void:Linkset .
                { 	 ?uri
                           alivocab:alignsSubjects ?s_prop ;
                           alivocab:alignsObjects ?o_prop .

                    BIND('oneAligns' as ?lkst_type_)
                    filter (isBlank(?s_prop) = "FALSE"^^xsd:boolean && isBlank(?o_prop) = "FALSE"^^xsd:boolean)
                }

                ### SELECTING CREATED LENS OR LINKSETS
              	UNION
                {
                     ?uri
                           alivocab:alignsSubjects ?s_prop ;
                           alivocab:alignsObjects ?o_prop .

                    BIND('multipleAligns' as ?lkst_type_)
                    filter (isBlank(?s_prop) = "TRUE"^^xsd:boolean || isBlank(?o_prop) = "TRUE"^^xsd:boolean)

                }
            """
    elif type == "linksetMultiD":
        type_filter = """?uri   rdf:type	void:Linkset .
                     ?uri
                           alivocab:hasAlignmentTarget  ?target  .

                     BIND('multidimensional' as ?lkst_type_)
            """
    elif type == "linkset":
        type_filter = """
        # THAT ARE OF TYPE LINKSET
        ?uri  rdf:type	void:Linkset
        BIND('oneAligns' as ?lkst_type_)
        #filter (isBlank(?s_prop) = "FALSE"^^xsd:boolean && isBlank(?o_prop) = "FALSE"^^xsd:boolean)
    """
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
    SELECT DISTINCT ?uri ?mode ?label ?lkst_type
    WHERE
    {{
        # GRAPH-TYPE FILTER
        {0}
        OPTIONAL {{?uri   skos:prefLabel		?label_ .}}
        BIND (IF(bound(?label_), ?label_ , "-") AS ?label)
        BIND (IF(bound(?lkst_type_), ?lkst_type_ , "-") AS ?lkst_type)

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


def get_filter_conditions(rq_uri, graph_uri, filter_uri='', filter_term='', useStardogApprox=True, graph_type='linkset'):
    # ADD FILTER CONDITIONS
    filter_condition = ""
    filter_count = ""
    filter_count_aux = ""

    if (rq_uri != '') and (graph_uri != ''):
        result = get_graph_filter(rq_uri, graph_uri, filter_uri)
        print result
        if result["result"]:
            method = result["result"][1][1]
            if method == "threshold":
                filter_condition = result["result"][1][0]
            else:
                filter_count = " GROUP BY ?sub ?pred ?obj "
                filter_count += result["result"][1][0]
                if method == "accept":
                    filter_count_aux = """
                    OPTIONAL {{ ?pred2 <http://risis.eu/alignment/predicate/hasValidation> ?accept.
                                ?accept rdf:type <http://www.w3.org/ns/prov#Accept> .
                             }}"""
                # TODO: CHANGE RISIS PREDICATE TO RISIS CLASS FOR REJECT
                elif method == "reject":
                    filter_count_aux = """
                    OPTIONAL {{?pred2 <http://risis.eu/alignment/predicate/hasValidation> ?reject.
                                ?reject rdf:type <http://risis.eu/alignment/predicate/Reject> .
                             }}"""
                elif method == "strength":
                    filter_count_aux = """
                    OPTIONAL {{ ?pred prov:wasDerivedFrom ?derivedFrom. }}"""

    # ADD FILTER TERM MATCH
    filter_term_match = ''
    if (filter_term != '') and (graph_uri != '') and (filter_term.__contains__("Type a term ") is False):

        if graph_type == 'linkset': ## Todo: check if it's enough
            prop_query = linkset_aligns_prop(graph_uri)
            prop_matrix = sparql_matrix(prop_query)["result"]
            if len(prop_matrix) > 1:
                alignsSubjects = "<{}>".format(prop_matrix[1][0]) if prop_matrix[1][0].__contains__(">/<") is False else prop_matrix[1][0]
                alignsObjects = "<{}>".format(prop_matrix[1][1]) if prop_matrix[1][1].__contains__(">/<") is False else prop_matrix[1][1]
                subjectsTarget = "<{}>".format(prop_matrix[1][3]) if prop_matrix[1][3].__contains__(">/<") is False else prop_matrix[1][3]
                objectsTarget = "<{}>".format(prop_matrix[1][4]) if prop_matrix[1][4].__contains__(">/<") is False else prop_matrix[1][4]
            else:
                print 'Problems getting metadata for linkset'
                return {}
        else:
            prop_query = get_target_datasets(graph_uri, Ut.from_alignment2singleton(graph_uri))
            prop_matrix = sparql_matrix(prop_query)["result"]
            if len(prop_matrix) > 1:
                subjectsTarget = "<{}>".format(prop_matrix[1][0]) if prop_matrix[1][0].__contains__(">/<") is False else prop_matrix[1][0]
                objectsTarget = "<{}>".format(prop_matrix[1][1]) if prop_matrix[1][1].__contains__(">/<") is False else prop_matrix[1][1]
                alignsSubjects = "<{}>".format(prop_matrix[1][2]) if prop_matrix[1][2].__contains__(">/<") is False else prop_matrix[1][2]
                alignsObjects = "<{}>".format(prop_matrix[1][3]) if prop_matrix[1][3].__contains__(">/<") is False else prop_matrix[1][3]
            else:
                print 'Problems getting metadata for lens'
                return {}

        if useStardogApprox:
            filter_term_match += """
        {{
        ## MATCH USING ALIGNED PROPERTY IN THE SUBJECT-DATASET
        GRAPH {1}
            {{
                ?sub    {3}     ?Svalue .
                #(?Svalue ?score) <tag:stardog:api:property:textMatch> \"\"\"{0}\"\"\".
                FILTER REGEX (STR(?Svalue), "{0}", "i" )
            }}
        }}
        UNION
        {{
        ## MATCH USING ALIGNED PROPERTY IN THE OBJECT-DATASET
        GRAPH {2}
            {{
                ?obj    {4}     ?Ovalue .
                #(?Ovalue ?score) <tag:stardog:api:property:textMatch> \"\"\"{0}\"\"\".
                FILTER REGEX (STR(?Ovalue), "{0}", "i" )
            }}
        }}
        """.format(filter_term, subjectsTarget, objectsTarget, alignsSubjects, alignsObjects)
        else:
            filter_term_match += """
        {{
        ## MATCH USING ALIGNED PROPERTY IN THE SUBJECT-DATASET
        GRAPH {1}
            {{
                ?sub    {3}     \"\"\"{0}\"\"\".
            }}
        }}
        UNION
        {{
        ## MATCH USING ALIGNED PROPERTY IN THE OBJECT-DATASET
        GRAPH {2}
            {{
                ?obj    {4}     \"\"\"{0}\"\"\".
            }}
        }}
        """.format(filter_term, subjectsTarget, objectsTarget, alignsSubjects, alignsObjects)

    return {'filter_condition': filter_condition,
            'filter_count': filter_count,
            'filter_count_aux': filter_count_aux,
            'filter_term_match': filter_term_match}


def get_correspondences(rq_uri, graph_uri, filter_uri='', filter_term='', limit=100, useStardogApprox=True, graph_type='linkset'):

    filters = get_filter_conditions(rq_uri, graph_uri, filter_uri, filter_term, useStardogApprox=useStardogApprox, graph_type=graph_type)
    # print 'FILTERS:', filters

    if graph_type == 'linkset':
        query = PREFIX + """
        ### GET CORRESPONDENCES
        SELECT DISTINCT ?sub ?pred ?obj
        {{
            GRAPH <{1}> {{ ?sub ?pred ?obj }}
            GRAPH <{6}> {{ ?pred ?p ?o .
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
        """.format(limit, graph_uri, filters['filter_condition'],
               filters['filter_count'], filters['filter_count_aux'],
               filters['filter_term_match'], Ut.from_alignment2singleton(graph_uri))
    else:
        query = PREFIX + """
        ### GET CORRESPONDENCES
        SELECT DISTINCT ?sub ?pred ?obj
        {{
            GRAPH <{1}> {{ ?sub ?pred ?obj }}
            GRAPH <{6}> {{ ?pred prov:wasDerivedFrom* ?pred2 .
                       ?pred2 ?p ?o .
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
        """.format(limit, graph_uri, filters['filter_condition'],
               filters['filter_count'], filters['filter_count_aux'],
               filters['filter_term_match'], Ut.from_alignment2singleton(graph_uri))

    if DETAIL:
        print query
    return query


def get_correspondences3(rq_uri, graph_uri, filter_uri='', filter_term='', limit=100, useStardogApprox=True):

    filters = get_filter_conditions(rq_uri, graph_uri, filter_uri, filter_term, useStardogApprox=useStardogApprox)

    query = PREFIX + """
    ### GET CORRESPONDENCES
    SELECT DISTINCT ?sub ?pred ?obj ?source ?target ?source_aligns ?target_aligns
    {{
        GRAPH <{1}> {{ ?sub ?pred ?obj }}
        GRAPH <{6}> {{ ?pred prov:wasDerivedFrom* ?pred2 .
                  ?pred2 ?p ?o ;
                  void:subjectsTarget ?source ;
                  void:objectsTarget ?target ;
                  alivocab:alignsSubjects ?source_aligns ;
                  alivocab:alignsObjects ?target_aligns .
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
    """.format(limit, graph_uri, filters['filter_condition'],
               filters['filter_count'], filters['filter_count_aux'],
               filters['filter_term_match'], Ut.from_alignment2singleton(graph_uri))
    if DETAIL:
        print query
    return query


def get_target_datasets(graph_uri='', singleton_uri=''):
    query = """
    ### GET TARGET DATASETS
    ### THIS FUNCTION EXTRACTS THE TARGET DATASETS INVOLVED IN THE CREATION OF A CORRESPONDENCE
    {0}
    SELECT DISTINCT ?DatasetsSub ?DatasetsObj ?alignsSubjects ?alignsObjects ?alignsMechanism
    where
    {{
        ### Retrieves the lens
        <{1}>  (prov:wasDerivedFrom|void:target|void:subjectsTarget|void:objectsTarget)*   ?graph1.

        {{ ?graph1
           void:subjectsTarget 			?DatasetsSub ;
           alivocab:alignsSubjects   	?alignsSubjects .
        ?graph1
           void:objectsTarget  			?DatasetsObj ;
            OPTIONAL {{ ?graph1    alivocab:alignsObjects    ?alignsObj }}
        }}


        BIND (IF(bound(?alignsObj), ?alignsObj , "resource identifier") AS ?alignsObjects)

        OPTIONAL {{ ?graph1	  alivocab:alignsMechanism  ?alignsMechanism1 }}


        FILTER NOT EXISTS {{
              {{ ?DatasetsSub  a  void:Linkset }}
               UNION
               {{ ?DatasetsSub  a  bdb:Lens }} }}
        FILTER NOT EXISTS {{
              {{ ?DatasetsObj  a  void:Linkset }}
               UNION
               {{ ?DatasetsObj  a  bdb:Lens }} }}
    }}
    """.format(PREFIX, graph_uri, singleton_uri)  # union)

    if DETAIL:
        print query
    return query


def get_target_datasets_old(graph_uri=''):

    query = """
    ### GET TARGET DATASETS
    ### THIS FUNCTION EXTRACTS THE TARGET DATASETS INVOLVED IN THE CREATION OF A CORRESPONDENCE
    {}
    SELECT DISTINCT ?graph ?subjectsTarget ?objectsTarget ?alignsSubjects ?alignsObjects ?alignsMechanism 
    where
    {{
            ### Retrieves the lens 
            <{}>  (void:target|void:subjectsTarget|void:objectsTarget)*   ?graph.

        ### Once we find those graphs, it means that we can extract the same source
        ### and target datasets that hold details about the entities being linked
        ?graph
           void:subjectsTarget 			?subjectsTarget ;
           void:objectsTarget  			?objectsTarget ;
           alivocab:alignsSubjects   ?alignsSubjects .
        OPTIONAL {{ ?graph	  alivocab:alignsMechanism  ?alignsMechanism }}
        OPTIONAL {{ ?graph    alivocab:alignsObjects    ?alignsObjS }}
        
        GRAPH ?graph
        {{ ?sub ?pred ?obj
        }}

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
    """.format(PREFIX, graph_uri)

    if DETAIL:
        print query
    return query


def get_evidences(graph_name, singleton, predicate=None):

    variable = ""
    # pred = ""
    if predicate is None:
        variable = "?pred"
        pred = "?pred"
    else:
        pred = predicate

    singleton_graph = "{}{}".format(Ns.singletons, Ut.get_uri_local_name(graph_name))
    # singleton_graph = str(graph_name).replace('lens','singletons')

    query = PREFIX + """
    ### GET EVIDENCES FOR SINGLETON
    SELECT DISTINCT {0} ?obj 
    {{
        GRAPH <{3}>
        {{
            <{1}>   <http://www.w3.org/ns/prov#wasDerivedFrom>*   ?x
            {{
                    ?x {2} ?obj .
                    MINUS
                    {{
                        ?x <http://risis.eu/alignment/predicate/hasValidation> ?obj
                    }}
            }}
            UNION
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
    """.format(variable, singleton, pred, singleton_graph)
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
                pred = predicate[i] if Ut.is_nt_format(predicate[i]) else "<{}>".format(predicate[i])
                triples += "\n\tOPTIONAL{{ <{}> {} ?obj_{} . }}".format(resource, pred, i)
        # print "TRIPLES", triples

    elif type(predicate) is str:
        if predicate != "resource identifier":
            pred = predicate if Ut.is_nt_format(predicate) else "<{}>".format(predicate)
            triples += "\n\tOPTIONAL{{ <{}> {} ?obj . }}".format(resource, pred)

    query = """
    ### GET RESOURCE DESCRIPTION
    SELECT DISTINCT *
    {{
        GRAPH <{}>
        {{ <{}> a _:type .
        {}
        }}
    }}
    """.format(graph, resource, triples)
    if DETAIL:
        print query
    return query


def get_predicates(graph, type=None, total=None, propPath=None, sub_uri='', search_pred='', search_text=''):

    if type:
        type_query = '?s a <{}> .'.format(type)
    else:
        type_query = ''

    # print "TOTAL:", total
    if total:
        opt_query = '(floor(count(distinct ?s)/{}*100) as ?ratio) ((?ratio)<100 as ?optional)'.format(str(total))
        # opt_query = '(count(distinct ?s)/{} as ?ratio) (((?ratio)-floor(?ratio))>0 as ?optional)'.format(str(total))
    else:
        opt_query = ''

    if propPath:
        propPath_query = '?sub {} ?s .'.format(propPath)
    else:
        propPath_query = ''

    if (search_pred) and (search_text):
        search_query = """
        ## TEXT SEARCH
        ?s    <{}>     ?Svalue .
        (?Svalue ?score) <tag:stardog:api:property:textMatch> \"\"\"{}\"\"\".
        """.format(search_pred, search_text)
    else:
        search_query = ''

    if sub_uri:
        if propPath:
            bind_query = """
            ## BIND
            BIND (<{}> AS  ?sub )
            """.format(sub_uri)
        else:
            bind_query = """
            ## BIND
            BIND (<{}> AS  ?s )
            """.format(sub_uri)
    else:
        bind_query = ''

    query = """
    ### GET PREDICATES WITHIN A CERTAIN GRAPH WITH EXAMPLE VALUE
    SELECT ?pred (MAX(?o) AS ?obj) {}
    {{
        GRAPH <{}>
        {{
            {}
            {}{}
            ?s ?pred ?o .

            {}
        }}
        FILTER (lcase(str(?o)) != 'null')
    }} GROUP BY ?pred
    """.format(opt_query, graph, bind_query, type_query, propPath_query, search_query)
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
            ?s ?uri ?o .
        }}
        {}
    }} 
    """.format(graph, filter)
    if DETAIL:
        print query
    return query


def get_dataset_predicate_values(graph, predicate, search_text=''):

    if search_text:
        search_query = """
        ## TEXT SEARCH
        ## (?value ?score) <tag:stardog:api:property:textMatch> \"\"\"{}\"\"\".
        """.format(search_text)
        select = 'DISTINCT (?s as ?uri) (?s as ?id) (?value as ?description) '
    else:
        search_query = ''
        select = 'distinct (?value as ?uri) #named uri just for reusing the html template'

    predicate = predicate if Ut.is_nt_format(predicate) else "<{}>".format(predicate)

    query = """
    ### GET DISTINCT VALUES OF FOR A PREDICATE WITHIN A CERTAIN GRAPH
    SELECT  {}
    {{
        GRAPH <{}>
        {{
            ?s {} ?value .

            #{}
            FILTER REGEX (?value, ".*{}.*", "i" )
        }}
    }} 
    """.format(select, graph, predicate, search_query, search_text)
    if DETAIL:
        print query
    return query


def get_aligned_predicate_value(source_uri, target_uri, src_aligns_list, trg_aligns_list):

    sub_qry = ''
    for i in range(len(src_aligns_list)):
        src_aligns = src_aligns_list[i]
        trg_aligns = trg_aligns_list[i]

        if src_aligns != 'none':
            src_aligns = "<{}>".format(src_aligns) if Ut.is_nt_format(src_aligns) is not True else src_aligns
            sub_qry += """ {{ GRAPH ?g_source
                                    {{  <{0}>  {1}  ?srcPredValue
                                        bind ("{1}" as ?alignsSubjects )
                                    }}

                            """.format(source_uri, src_aligns)
        else:
            sub_qry += """
                          BIND ("{1}" as ?alignsSubjects )
                          BIND ("{1}" AS ?srcPredValue)
                        }}
                        """.format(target_uri, trg_aligns)
        if trg_aligns != 'none':
            trg_aligns = "<{}>".format(trg_aligns) if Ut.is_nt_format(trg_aligns) is not True else trg_aligns

            sub_qry += """
                        OPTIONAL
                        {{  GRAPH ?g_target
                                {{  <{0}>  {1}  ?trgPredVal_
                                 }}
                        }}  BIND ("{1}" as ?alignsObjects )
                            BIND (IF ({1} = <http://risis.eu/alignment/predicate/resourceIdentifier>, <{0}>, ?trgPredVal_) AS ?trgPredVal)
                        }}
                        """.format(target_uri, trg_aligns)
        else:
            sub_qry += """
                          BIND ("{1}" as ?alignsObjects )
                          BIND ("{1}" AS ?trgPredVal)
                        }}
                        """.format(target_uri, trg_aligns)

        if i < len(src_aligns_list)-1:
            sub_qry += ' UNION '


    query = """
    ### GET VALUES OF ALIGNED PREDICATES
    SELECT DISTINCT ?srcPredValue ?trgPredValue ?alignsSubjects ?alignsObjects
    {{
        #QUERY COMPOSED WITH LIST OF PREDICATES
        {}

        # FILTER((?g_source) != (?g_target))
        BIND (IF(bound(?trgPredVal), ?trgPredVal , "") AS ?trgPredValue)
    }}
    """.format(sub_qry)
    if DETAIL:
        print query
    return query


def get_linkset_corresp_sample_details(linkset, limit=1, crossCheck=True):

    source = ""
    source_bind = ""
    target = ""
    target_bind = ""
    prop_query = linkset_aligns_prop(linkset, cross_check=crossCheck)
    prop_matrix = sparql_matrix(prop_query)["result"]

    s_ds = "<{}>".format(prop_matrix[1][3])
    t_ds = "<{}>".format(prop_matrix[1][4])
    crossCheck = prop_matrix[1][5]

    query = PREFIX + """
    #### CORRESPONDENCE DETAIL SAMPLE

    SELECT ?sub_uri ?obj_uri
    (GROUP_CONCAT(DISTINCT ?s_PredV; SEPARATOR=" | ") as ?s_PredValue)
    (GROUP_CONCAT(DISTINCT ?o_PredV; SEPARATOR=" | ") as ?o_PredValue)
    ("{2}" as ?crossCheck)
    {{
        GRAPH  <{0}>
        {{
            ?sub_uri    ?aligns        ?obj_uri
        }}

        ###SOURCE SLOT

        ###TARGET SLOT

        BIND (IF(bound(?o_PredVal), ?o_PredVal , "none") AS ?o_PredV)
        BIND ("" AS ?operator)
    }} GROUP BY ?sub_uri ?obj_uri
    LIMIT {1}""".format(linkset, limit, crossCheck)

    for i in range(1, len(prop_matrix)):
        src = "<{}>".format(prop_matrix[i][0]) if prop_matrix[i][0].__contains__(">/<") is False else prop_matrix[i][0]
        trg = "<{}>".format(prop_matrix[i][1]) if prop_matrix[i][1].__contains__(">/<") is False else prop_matrix[i][1]

        # mec = prop_matrix[i][2]
        if i == 1:

            source = "?sub_uri  {}  ?s_PredV_{} .".format(src, str(i))

            if str(trg).__contains__('resourceIdentifier'):
                target += "\n\t\t\t\t\t\t\tBIND (?obj_uri  as  ?o_PredVal_{} ).".format(str(i))
            else:
                target += "\n\t\t\t\t\t\t\t?obj_uri  {}  ?o_PredVal_{} . #! ".format(trg, str(i))

            # if mec == 'http://risis.eu/mechanism/identity':
            #
            #     source_bind = "\n\t\t\t\t\t\tBIND(CONCAT(\"[\", STR(?sub_uri)"
            #     target_bind = "\n\t\t\t\t\t\t\tBIND(CONCAT(\"[\", STR(?obj_uri)"
            # else:

            source_bind = "\n\t\t\t\t\t\tBIND(CONCAT(\"[\", STR(?s_PredV_{})".format(str(i))
            target_bind = "\n\t\t\t\t\t\t\tBIND(CONCAT(\"[\", STR(?o_PredVal_{})".format(str(i))
        else:

            source += "\n\t\t\t\t\t\t?sub_uri  {}  ?s_PredV_{} .".format(src, str(i))

            if str(trg).__contains__('resourceIdentifier'):
                target += "\n\t\t\t\t\t\t\tBIND (?obj_uri  as  ?o_PredVal_{} ).".format(trg, str(i))
            else:
                target += "\n\t\t\t\t\t\t\t?obj_uri  {}  ?o_PredVal_{} . #! ".format(trg, str(i))

            # if mec == 'http://risis.eu/mechanism/identity':
            #     source_bind += ", \"|\", STR(?sub_uri)"
            #     target_bind += ", \"|\",  STR(?obj_uri)"
            # else:

            source_bind += ", \"|\", STR(?s_PredV_{})".format(str(i))
            target_bind += ", \"|\",  STR(?o_PredVal_{})".format(str(i))


    source_bind += ", \"]\" ) AS ?s_PredV )"
    target_bind += ", \"]\" ) AS ?o_PredVal )"
    source += source_bind
    target += target_bind

    source = """ GRAPH {}
        {{
            {}
        }}""".format(s_ds, source)

    if target.__contains__('#!'): ## marker added to make sure there is at list one pattern to match
        target = """ #OPTIONAL
        {{
            graph {}
            {{
                {}
            }}
        }}""" .format(t_ds, target)

    query = str(query).replace("###SOURCE SLOT", source).replace("###TARGET SLOT", target)
    print query
    return query


def get_linksetCluster_corresp_sample_details(linkset, limit=1, crossCheck=True):

    source = ""
    source_bind = ""
    target = ""
    target_bind = ""
    # prop_query = linksetCluster_aligns_prop(linkset)
    # prop_matrix = sparql_matrix(prop_query)["result"]
    #
    # s_ds = "<{}>".format(prop_matrix[1][3])
    # t_ds = "<{}>".format(prop_matrix[1][4])
    # crossCheck = prop_matrix[1][5]

    # REMOVED
    # """
    # ;
    #                      alivocab:alignsSubjects			?alignsSubjects;
    #                      alivocab:alignsObjects			?alignsObjects
    # """

    query = PREFIX + """
    #### CORRESPONDENCE DETAIL SAMPLE

    SELECT ?subjectsTarget ?alignsSubjects ?valueSubj ?objectsTarget ?alignsObjects ?valueObj
    {{
        GRAPH  <{0}>
        {{
            ?sub    ?singProp        ?obj
        }}

        GRAPH <{1}> {{

              ?singProp  void:subjectsTarget		?subjectsTarget ;
                         void:objectsTarget			?objectsTarget .
            }}

			GRAPH ?subjectsTarget
            {{
            	?sub 	?p1			?valueSubj.
                bind(iri(concat('<', str(?p1),'>')) as ?alignsSubjects)
            }}

			GRAPH ?objectsTarget
            {{
            	?obj 	?p2			?valueObj.
                bind(iri(concat('<', str(?p2),'>')) as ?alignsObjects)
            }}
    }}
    LIMIT {2}""".format(linkset, Ut.from_alignment2singleton(linkset), limit)

    print query
    return query


def get_linkset_corresp_details(linkset, limit=1, rq_uri='', filter_uri='', filter_term='', type='oneAligns', count=True):

    filters = get_filter_conditions(rq_uri, linkset, filter_uri, filter_term)
    # print 'FILTERS:', filters

    count_query = ''
    if count is True:
        count_query = """
                    SELECT DISTINCT (count(DISTINCT ?pred ) as  ?triples)
                    {{
                        GRAPH <{0}> {{ ?sub ?pred ?obj }}
                        GRAPH <{5}> {{ ?pred prov:wasDerivedFrom* ?pred2 .
                                   ?pred2 ?p ?o .
                            # ADDITIONAL PATTERNS TO ALLOW FOR FILTER COUNT
                            {3}
                        }}

                        # FILTER BY CONDITION
                        {1}

                        # FILTER BY TERM MATCH
                        {4}

                    }}
                    # FILTER BY COUNT
                    {2}
        """.format(linkset, filters['filter_condition'],
                   filters['filter_count'], filters['filter_count_aux'],
                   filters['filter_term_match'], Ut.from_alignment2singleton(linkset))

    if type == 'oneAligns':
        query = PREFIX + """
        ### LINKSET DETAILS

        SELECT DISTINCT
        (GROUP_CONCAT(DISTINCT ?s_prop; SEPARATOR=" | ") as ?s_property_list)
        (GROUP_CONCAT(DISTINCT ?o_prop; SEPARATOR=" | ") as ?o_property_list)
        (GROUP_CONCAT(?mec; SEPARATOR=" | ") as ?mechanism_list)
        #(GROUP_CONCAT(?triple; SEPARATOR=" | ") as ?triples)
        ?subTarget ?objTarget ?s_datatype ?o_datatype ?triples ?operator
        ?threshold ?delta ?dist ?dist_unit
        ?s_property ?o_property ?mechanism
        ?s_crossCheck_property ?o_crossCheck_property
        WHERE {{
            bind (<{0}> as ?graph)
            ?graph
                (prov:wasDerivedFrom/void:target)*/prov:wasDerivedFrom*       ?linkset ;
                alivocab:alignsSubjects     ?s_property_;
                alivocab:alignsObjects      ?o_property_ ;
                alivocab:alignsMechanism    ?mechanism .
            ?linkset
                alivocab:alignsMechanism    ?mec ;
                void:subjectsTarget         ?subTarget ;
                bdb:subjectsDatatype        ?s_datatype ;
                alivocab:alignsSubjects     ?s_prop;
                void:objectsTarget          ?objTarget ;
                bdb:objectsDatatype         ?o_datatype ;
                alivocab:alignsObjects      ?o_prop .
                #void:triples               ?triple .

            OPTIONAL {{
                ?linkset      alivocab:crossCheckSubject  ?s_crossCheck_property_ .
            }}

            OPTIONAL {{
                ?linkset      alivocab:crossCheckObject   ?o_crossCheck_property_ .
            }}

              BIND (IF(bound(?s_crossCheck_property_), ?s_crossCheck_property_, ?s_property_) as ?s_property).
              BIND (IF(bound(?o_crossCheck_property_), ?o_crossCheck_property_, ?o_property_) as ?o_property).

            OPTIONAL {{
                <{0}>
                alivocab:threshold          ?threshold_ ;
                alivocab:delta              ?delta_ .
            }}

                BIND (IF(bound(?s_crossCheck_property_), ?s_crossCheck_property_ , '') AS ?s_crossCheck_property)
                BIND (IF(bound(?o_crossCheck_property_), ?o_crossCheck_property_ , '') AS ?o_crossCheck_property)

                BIND (IF(bound(?threshold_), ?threshold_ , 0) AS ?threshold)
                BIND (IF(bound(?delta_), ?delta_ , '') AS ?delta)
                BIND (IF(bound(?unit_), ?unit_ , '') AS ?dist_unit)
                BIND (IF(bound(?unit_value_), ?unit_value_ , '') AS ?dist)
                BIND ("" AS ?operator)

                # COUNT TRIPLES ACCORDING TO FILTER
                {{ {2} }}

            }}
        GROUP BY ?subTarget ?objTarget ?s_datatype ?o_datatype ?triples
        ?operator
        ?s_property ?o_property ?mechanism ?threshold ?delta ?dist ?dist_unit
        ?s_crossCheck_property ?o_crossCheck_property
        # LIMIT {1}
        """.format(linkset, limit, count_query)
    else:
        query = PREFIX + """
        ### LINKSET DETAILS

        SELECT DISTINCT
        (GROUP_CONCAT(DISTINCT ?s_prop; SEPARATOR=" | ") as ?s_property_list)
        (GROUP_CONCAT(DISTINCT ?o_prop; SEPARATOR=" | ") as ?o_property_list)
        (GROUP_CONCAT(?mec; SEPARATOR=" | ") as ?mechanism_list)
        #(GROUP_CONCAT(?triple; SEPARATOR=" | ") as ?triples)
        ?subTarget ?objTarget ?s_datatype ?o_datatype ?triples ?operator
        #?sub_uri ?obj_uri ?s_PredValue ?o_PredValue
        ?threshold ?delta ?dist ?dist_unit
        ?s_property ?o_property ?mechanism
        ?s_crossCheck_property ?o_crossCheck_property
        WHERE {{
            bind (<{0}> as ?graph)
            ?graph
                # (prov:wasDerivedFrom/void:target)*/prov:wasDerivedFrom*       ?linkset ;
                # Temporarilly changed due to strange result in windows computer
                # after adding the union for addressing list of aligns-properties.
                # To be further checked because this affects the visulisation of
                # linkset that are derived from other alignments,
                # e.g. showing several times the mechanism
                prov:wasDerivedFrom*/void:target*/prov:wasDerivedFrom*       ?linkset ;
                alivocab:alignsMechanism    ?mechanism .
            ?linkset
                alivocab:alignsMechanism    ?mec ;
                void:subjectsTarget         ?subTarget ;
                bdb:subjectsDatatype        ?s_datatype ;
                void:objectsTarget          ?objTarget ;
                bdb:objectsDatatype         ?o_datatype .

          {{ select ?graph ?linkset
                        (GROUP_CONCAT(DISTINCT ?s_prop_; SEPARATOR=" | ") as ?s_prop)
                        (GROUP_CONCAT(DISTINCT ?o_prop_; SEPARATOR=" | ") as ?o_prop)
                         ?s_property ?o_property ?s_crossCheck_property_ ?o_crossCheck_property_
          {{

            {{ ?linkset    alivocab:alignsSubjects     ?SRC_onj .
            ?SRC_onj    rdf:rest*/rdf:first         ?s_prop_ .
            ?linkset      alivocab:crossCheckSubject  ?s_property .
            ?linkset      alivocab:crossCheckSubject  ?s_crossCheck_property_ .

            ?linkset    alivocab:alignsObjects      ?trg_onj .
            ?trg_onj    rdf:rest*/rdf:first         ?o_prop_ .
            ?linkset      alivocab:crossCheckObject   ?o_property .
            ?linkset      alivocab:crossCheckObject   ?o_crossCheck_property_ .

            }}
            UNION
            {{
              ?linkset    alivocab:alignsSubjects     ?s_prop_ .
              OPTIONAL {{?linkset      alivocab:crossCheckSubject  ?s_property }} .
              OPTIONAL {{?linkset      alivocab:crossCheckSubject  ?s_crossCheck_property_ }} .

              ?linkset    alivocab:alignsObjects      ?o_prop_ .
              OPTIONAL {{?linkset      alivocab:crossCheckObject   ?o_property}} .
              OPTIONAL {{?linkset      alivocab:crossCheckObject   ?o_crossCheck_property_ }} .
            }}

            filter (isBlank(?s_prop_) = "FALSE"^^xsd:boolean) .
            filter (isBlank(?o_prop_) = "FALSE"^^xsd:boolean) .


          }} GROUP BY ?graph ?linkset ?s_property ?o_property ?s_crossCheck_property_ ?o_crossCheck_property_
          }}


            OPTIONAL {{
                <{0}>
                alivocab:threshold          ?threshold_ .
            }}
            OPTIONAL {{
                <{0}>
                alivocab:delta              ?delta_ .
            }}
            OPTIONAL {{
                <{0}>
                alivocab:unit                   ?unit_ .
            }}
            OPTIONAL {{
                <{0}>
                alivocab:unitValue              ?unit_value_ .
            }}

                BIND (IF(bound(?s_crossCheck_property_), ?s_crossCheck_property_ , '') AS ?s_crossCheck_property)
                BIND (IF(bound(?o_crossCheck_property_), ?o_crossCheck_property_ , '') AS ?o_crossCheck_property)

                BIND (IF(bound(?threshold_), ?threshold_ , 0) AS ?threshold)
                BIND (IF(bound(?delta_), ?delta_ , '') AS ?delta)
                BIND (IF(bound(?unit_), ?unit_ , '') AS ?dist_unit)
                BIND (IF(bound(?unit_value_), ?unit_value_ , '') AS ?dist)
                BIND ("" AS ?operator)

                # COUNT TRIPLES ACCORDING TO FILTER
                {{ {2} }}

            }}
        GROUP BY ?subTarget ?objTarget ?s_datatype ?o_datatype ?triples
        #?sub_uri ?obj_uri ?s_PredValue ?o_PredValue
        ?operator
        ?s_property ?o_property ?mechanism ?threshold ?delta ?dist ?dist_unit
        ?s_crossCheck_property ?o_crossCheck_property
        # LIMIT {1}
        """.format(linkset, limit, count_query)

    if True:
        print query
    return query


def get_linksetCluster_corresp_details(linkset, limit=1, rq_uri='', filter_uri='', filter_term=''):

    filters = get_filter_conditions(rq_uri, linkset, filter_uri, filter_term)
    # print 'FILTERS:', filters

    count_query = """
                SELECT DISTINCT (count(DISTINCT ?pred ) as  ?triples)
                {{
                    GRAPH <{0}> {{ ?sub ?pred ?obj }}
                    GRAPH <{5}> {{ ?pred prov:wasDerivedFrom* ?pred2 .
                               ?pred2 ?p ?o .
                        # ADDITIONAL PATTERNS TO ALLOW FOR FILTER COUNT
                        {3}
                    }}

                    # FILTER BY CONDITION
                    {1}

                    # FILTER BY TERM MATCH
                    {4}

                }}
                # FILTER BY COUNT
                {2}
    """.format(linkset, filters['filter_condition'],
               filters['filter_count'], filters['filter_count_aux'],
               filters['filter_term_match'], Ut.from_alignment2singleton(linkset))

    query = PREFIX + """
    ### LINKSET DETAILS

     SELECT DISTINCT ?mechanism ?triples
	(GROUP_CONCAT(DISTINCT ?property; SEPARATOR=" | ") as ?properties)
		?dataset ?datatype
    WHERE {{
        bind (<{0}> as ?graph)
        ?graph
            (prov:wasDerivedFrom/void:target)*/prov:wasDerivedFrom*       ?linkset ;
            alivocab:alignsMechanism    ?mechanism .
        ?linkset
            alivocab:alignsMechanism    ?mec ;
            alivocab:hasAlignmentTarget  ?target .
		?target
                alivocab:hasTarget  	?dataset ;
                alivocab:hasDatatype   	?datatype ;
                alivocab:aligns		    ?property .

            # COUNT TRIPLES ACCORDING TO FILTER
            {{ {2} }}

        }}
    GROUP BY ?triples ?mechanism ?linkset ?dataset ?datatype
    # LIMIT {1}
    """.format(linkset, limit, count_query)

    if DETAIL:
        print query
    return query


def check_graph_dependencies_rq(rq_uri, graph_uri):
    query = PREFIX + """
    ### CHECK LINKSET/LENS DEPENDENCIES
    
    SELECT ?uri ?type
    {{  
        {{
          ?uri 	a 			    ?type;
                prov:wasDerivedFrom|void:target|void:subjectsTarget|void:objectsTarget     <{1}>.

          GRAPH <{0}>
          {{
                ?s alivocab:created|prov:used ?uri.
          }}
        }} UNION {{
          GRAPH <{0}>
          {{
              ?uri a		?type;
                   alivocab:hasViewLens/alivocab:selected <{1}>.
          }}      
        }}
    }}  ORDER BY ?type   
    """.format(rq_uri, graph_uri)
    print query
    return query


def get_delete_filter(rq_uri, filter_uri):
    query = PREFIX + """
    # DELETE THE FILTER
    DELETE
    {{
      GRAPH ?rq
      {{
            ?rq       alivocab:created    ?filter .
            ?filter     ?pred                ?obj .
      }}
    }}
    WHERE
    {{
      BIND(<{0}> AS ?rq) .
      BIND(<{1}> AS ?filter) .
      GRAPH ?rq
      {{
            ?rq       alivocab:created    ?filter .
            ?filter     ?pred                ?obj .
      }}
    }}
    """.format(rq_uri, filter_uri)
    print query
    return query


def get_delete_validation(rq_uri, graph_uri, singleton_uri):
    # there should be only one validation per rq
    query = PREFIX + """
    DELETE
    {{
      GRAPH ?singleton_graph
      {{
        ?rq	                <{3}> 	            ?validation .
        ?singleton_uri	    <{4}> 	            ?validation .
        ?validation        ?pre 		        ?obj .
      }}
    }}
    WHERE
    {{
      BIND(<{0}> AS ?rq_uri) .
      BIND(<{1}> AS ?singleton_graph) .
      BIND(<{2}> AS ?singleton_uri) .
      GRAPH ?singleton_graph
      {{
        ?rq	                <{3}> 	            ?validation .
        ?singleton_uri	    <{4}> 	            ?validation .
        ?validation        ?pre 		        ?obj .
      }}
    }}
    """.format(rq_uri, Ut.from_alignment2singleton(graph_uri), singleton_uri,
               "{}created".format(Ns.alivocab), "{}hasValidation".format(Ns.alivocab))
    print query
    return query


def delete_view_rq(rq_uri, view_uri):
    query = PREFIX + """
    DELETE
    {{
      GRAPH ?rq
      {{
        ?rq	    alivocab:created 	?view .
        ?view   ?pre 		        ?obj .
        ?obj 	?predicate 	        ?object .
      }}
    }}
    WHERE
    {{
      BIND(<{0}> AS ?rq) .
      BIND(<{1}> AS ?view) .
      GRAPH ?rq
      {{
        ?rq     alivocab:created 	?view .
        ?view   ?pre                ?obj .
        OPTIONAL {{ ?obj ?predicate ?object }}

      }}
    }}
    """.format(rq_uri, view_uri)
    print query
    return query


def update_view_label_rq(rq_uri, view_uri, view_label):
    query = PREFIX + """
    DELETE
    {{
         GRAPH <{0}>
         {{
            <{1}>  skos:prefLabel ?value .
        }}
    }}
    WHERE
    {{
      GRAPH <{0}>
      {{
        <{1}>   skos:prefLabel  ?value.
      }}
    }} ;
    INSERT DATA
    {{
      GRAPH <{0}>
      {{
        <{1}>   skos:prefLabel  "{2}".
      }}   
    }}
    """.format(rq_uri, view_uri, view_label)
    print query
    return query


def update_label_rq(rq_uri, graph_uri, label):
    query = PREFIX + """
    DELETE
    {{
         GRAPH <{0}>
         {{
            <{1}>  skos:prefLabel ?value .
        }}
    }}
    WHERE
    {{
      GRAPH <{0}>
      {{
        <{1}>   skos:prefLabel  ?value.
      }}
    }} ;
    INSERT DATA
    {{
      GRAPH <{0}>
      {{
        <{1}>   skos:prefLabel  "{2}".
      }}
    }}
    """.format(rq_uri, graph_uri, label)
    print query
    return query


def get_lens_corresp_details(lens, limit=1):

    query = PREFIX + """
    ### LENS DETAILS AND VALUES OF ALIGNED PREDICATES

    SELECT DISTINCT ?mechanism ?subTarget ?s_datatype ?s_property
    ?objTarget ?o_datatype ?o_property ?s_PredValue ?o_PredValue ?triples ?operator
    ?s_property_list ?o_property_list ?s_crossCheck_property ?o_crossCheck_property
    WHERE
    {{

        <{0}>
             (void:target|void:subjectsTarget|void:objectsTarget)* ?x .
        ?x

            void:subjectsTarget            ?subTarget ;
            bdb:subjectsDatatype           ?s_datatype ;
            alivocab:alignsSubjects        ?s_property ;
            void:objectsTarget             ?objTarget ;
            bdb:objectsDatatype            ?o_datatype ;
            alivocab:alignsObjects         ?o_property .

        #<{0}>
        #    void:triples                   ?triples .

        BIND (?s_property AS ?s_property_list)
        BIND (?o_property AS ?o_property_list)

        {{
            select (count (?sing) as ?triples )
            where
            {{
                GRAPH <{0}>
                {{
                  ?sub ?sing ?obj .
                  #?sing ?pred ?sObj .
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
        BIND ("" AS ?s_crossCheck_property)
        BIND ("" AS ?o_crossCheck_property)
    }}
    LIMIT {1}""".format(lens, limit)
    if DETAIL:
        print query
    return query


# TODO: CHECK IF CAN BE REMOVED
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


def get_cluster_references():
    query = """
    PREFIX rdfs:    <{}>
    PREFIX ll:    <{}>

    SELECT DISTINCT (?uri as ?id) ?uri (GROUP_CONCAT(distinct ?label; SEPARATOR=" ") AS ?labels) (CONCAT( str(?uri), " | ", ?labels) as ?description)
   # SELECT DISTINCT ?uri ?label ?mode
    {{
        GRAPH  ?cluster
        {{
            ?cluster ll:hasReference ?uri .
            ?uri  rdfs:label ?label .
        }}
        #BIND("no-mode" as ?mode)
        # BIND (CONCAT( str(?uri), " | ", str(?label)) AS ?description)
    }} group by ?uri
    """.format(Ns.rdfs, Ns.alivocab)

    if DETAIL:
        print query
    return query


def get_cluster_references_table():
    query = """
    PREFIX rdfs:    <{}>
    PREFIX ll:    <{}>
    PREFIX void:    <{}>

    SELECT DISTINCT ?uri (?uri as ?id)
				(GROUP_CONCAT(distinct ?dataset; SEPARATOR=" | ") AS ?datasets)
				(GROUP_CONCAT(distinct ?label; SEPARATOR=" | ") AS ?labels)
				(count(distinct ?cluster) as ?clusters)
				(round(avg(?c)) as ?avgc) (max(?c) as ?maxc) (min(?c) as ?minc)
    {{
        GRAPH  ?cluster
        {{
            ?cluster ll:hasReference ?uri .
            ?uri  rdfs:label ?label .
			?cluster ll:hasConstraint ?constr .
            ?constr  void:target ?dataset .

          {{ select ?cluster ?uri (count(distinct ?o) as ?c)
            {{
   			  GRAPH  ?cluster
         	  {{
                  ?cluster ll:hasReference ?uri .
                  ?s ll:list ?o .
              }}
            }} group by ?uri ?cluster
          }}
        }}
        #BIND("no-mode" as ?mode)
        # BIND (CONCAT( str(?uri), " | ", str(?label)) AS ?description)
    }} group by ?uri
    order by ?labels
    """.format(Ns.rdfs, Ns.alivocab, Ns.void)

    if DETAIL:
        print query
    return query


def get_clusters_table(reference_uri):
    query = """
    PREFIX rdfs:    <{}>
    PREFIX ll:    <{}>
    PREFIX void:    <{}>

    SELECT DISTINCT ?uri (?uri as ?id)
				(GROUP_CONCAT(distinct ?dataset; SEPARATOR=" | ") AS ?datasets)
				(GROUP_CONCAT(distinct ?property; SEPARATOR=" | ") AS ?properties)
				(GROUP_CONCAT(distinct ?label; SEPARATOR=" | ") AS ?labels)
				(count(?o) as ?count)
				#(count(distinct ?o) as ?count)
    {{
        GRAPH  ?uri
        {{
            ?uri ll:hasReference <{}> .
            ?uri  rdfs:label ?label .
			?uri ll:hasConstraint ?constr .
            ?constr  void:target ?dataset ;
                      ll:hasProperty ?property.
            ?s ll:list ?o .
        }}
    }} group by ?uri
    order by ?labels
    """.format(Ns.rdfs, Ns.alivocab, Ns.void, reference_uri)

    if DETAIL:
        print query
    return query


def get_clusters_by_reference(reference_uri):
    query = """
    PREFIX ll:    <{}>

    SELECT DISTINCT ?uri ?label ?mode
    {{
        GRAPH  ?uri
        {{
            bind (<{}> as ?reference)
            ?uri ll:hasReference ?reference .
        }}
        BIND("no-mode" as ?mode)
        #BIND("-" as ?label)
        BIND(strafter(strafter(str(?uri),"cluster/"), "_") as ?label)
    }}
    """.format(Ns.alivocab, reference_uri)

    if DETAIL:
        print query
    return query


def get_cluster_metadata(reference_uri, cluster_uri):
    query = """
    PREFIX void:    <{}>
    PREFIX ll:    <{}>

    SELECT DISTINCT (?constr as ?id) (?constr as ?uri) ?description
    {{
        GRAPH  ?cluster
        {{
            bind (<{}> as ?reference)
            bind (<{}> as ?cluster)
            ?cluster ll:hasReference ?reference .
            ?cluster ll:hasConstraint ?constr .
            ?constr  void:target ?dataset;
        		     ll:hasValue ?value;
                     ll:hasProperty ?property.
        }}
        BIND (CONCAT( str(?dataset), " | ", str(?property), " | ", str(?value)) AS ?description)
    }}
    """.format(Ns.void, Ns.alivocab, reference_uri, cluster_uri)

    if DETAIL:
        print query
    return query


def get_datasets_per_reference(reference_uri):
    query = """
    PREFIX ll:    <{}>
    PREFIX void:    <{}>

    SELECT DISTINCT ?uri ?label ?mode
    {{
        GRAPH  ?uri
        {{
            bind (<{}> as ?reference)
            ?cluster ll:hasReference ?reference .
            ?cluster ll:hasConstraint ?constr .
            ?constr  void:target ?uri;
        }}
        BIND("no-mode" as ?mode)
        BIND("-" as ?label)
    }}
    """.format(Ns.alivocab, Ns.void, reference_uri)

    if DETAIL:
        print query
    return query


def get_clustered_objects(reference_uri, cluster_uri):
    query = """
    PREFIX void:    <{}>
    PREFIX ll:    <{}>

    SELECT DISTINCT (?object as ?uri) (?object as ?id) ?dataset (group_concat(distinct str(?p); SEPARATOR=" | ") as ?properties) (group_concat(str(?v); SEPARATOR=" | ") as ?values)
    {{
        graph ?dataset
        {{
          ?object ?p ?v .
        }}
        {{
          select ?object ?dataset (group_concat(str(?property)) as ?properties)
          {{
          bind (<{}> as ?cluster)
          GRAPH  ?cluster
          {{
                ?cluster ll:hasReference <{}> .
                ?cluster ll:hasConstraint ?constr ;
                       ll:list ?object.
                ?constr  void:target ?dataset;
                      ll:hasProperty ?property;
                      ll:hasValue ?value.
          }}
          }} group by ?object ?dataset
        }}
         FILTER (CONTAINS( ?properties, str(?p) ) )
    }} group by ?object ?dataset
    """.format(Ns.void, Ns.alivocab, cluster_uri, reference_uri)

    if DETAIL:
        print query
    return query


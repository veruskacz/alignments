import time
import xmltodict
import src.Alignments.Settings as St
import src.Alignments.NameSpace as Ns
from src.Alignments.Query import endpoint

#######################################################################################
# DROP GENERIC
#######################################################################################


def drop_linksets(display=False, activated=True):

    queries = """
    #################################################################
    ### DELETE LINKSET NAMED GRAPHS AND METADATA                  ###
    #################################################################

    ### 1. DELETING LINKTYPE METADATA
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX link:    <{}>

    DELETE {{ ?linktype ?x ?y }}
    where
    {{
      ?linkset
        a                   void:Linkset ;
        void:linkPredicate  ?linktype .
      ?linktype
        ?x ?y
    }} ;

    ### 2. DELETING ASSERTION METADATA
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      ?linkset
        a                       void:Linkset ;
        bdb:assertionMethod     ?assertionMethod .
      ?assertionMethod
        ?x ?y
    }} ;

    ### 3. DELETING JUSTIFICATION METADATA
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      ?linkset
        a                           void:Linkset ;
        bdb:linksetJustification    ?linksetJustification .
      ?linksetJustification
        ?x ?y
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      ?linkset
        a 							void:Linkset ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING LINKSET GRAPHS
    DELETE {{ ?linkset ?x ?y . }}
    where
    {{
      ?linkset a    void:Linkset ;
               ?x   ?y
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'linkset', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab)

    # print endpoint(queries, database_name, host)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING LINKSETS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "======================================================="
        )
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_subsets(display=False, activated=True):

    queries = """
    #################################################################
    ### DELETE LINKSET NAMED GRAPHS AND METADATA                  ###
    #################################################################

    ### 1. DELETING LINKTYPE METADATA
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX link:    <{}>
    DELETE {{ ?linktype ?x ?y }}
    where
    {{
      ?linkset
        a                   void:Linkset ;
        void:subset         ?subset ;
        void:linkPredicate  ?linktype .
      ?linktype
        ?x                  ?y
    }} ;

    ### 2. DELETING ASSERTION METADATA
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      ?linkset
        a                   void:Linkset ;
        void:subset         ?subset ;
        bdb:assertionMethod ?assertionMethod .
      ?assertionMethod
        ?x                  ?y
    }} ;

    ### 3. DELETING JUSTIFICATION METADATA
    DELETE {{?linksetJustification ?x ?y}}
    where
    {{
      ?linkset
        a                           void:Linkset ;
        void:subset                 ?subset ;
        bdb:linksetJustification    ?linksetJustification .
      ?linksetJustification
        ?x                          ?y
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      ?linkset
        a 							void:Linkset ;
        void:subset                 ?subset ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING LINKSET GRAPHS
    DELETE {{ ?linkset ?x ?y . }}
    where
    {{
      ?linkset
        a void:Linkset ;
        void:subset ?subset ;
        ?x ?y
    }};

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'subset', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab)

    if display is True:
        print queries

    # print endpoint(queries, database_name, host)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING SUBSETS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_lenses(display=False, activated=False):

    queries = """
    PREFIX void:    <{}>
    PREFIX bdb:     <{}>
    PREFIX link:    <{}>

    ### 1. DELETING ASSERTION METHOD
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lense ;
        bdb:assertionMethod 		?assertionMethod .
      ?assertionMethod ?x ?y .
    }} ;

    ### 2. DELETING JUSTIFICATION
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lense ;
        bdb:linksetJustification 	?linksetJustification ;.
      ?linksetJustification ?x ?y .
    }} ;

    ### 3. DELETING LINK-TYPE
    DELETE {{ ?linkPredicate ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lens ;
        void:linkPredicate 			?linkPredicate .
      ?linkPredicate ?x ?y .
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      ?linkset
        a 							bdb:Lens ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING THE METADATA
    DELETE {{ ?linkset ?x ?y }}
    where
    {{
      ?linkset
        a 							bdb:Lens ;
        ?x                          ?y.
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'lens', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING LENSES...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_all():
    print "{}{}{}".format(
        "\n====================================================================================\n",
        "List of graphs dropped\n",
        "===================================================================================="
    )

    drops = """
    #################################################################
    ### DELETE NAMED GRAPHS                                       ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
    }}
    """
    print drops

    print "{}{}{}".format(
        "\n=====================================================================\n",
        "DROPPING ALL...\nPLEASE WAIT FOR FEEDBACK.\n",
        "=====================================================================")
    print endpoint(drops)


def drop_unions(display=False, activated=False):

    queries = """
    PREFIX void:        <{}>
    PREFIX bdb:         <{}>
    PREFIX alivocab:    <{}>
    PREFIX lensOp:      <{}>

    ### DELETING THE METHOD RESOURCE
    DELETE {{ ?method ?x ?y }}
    WHERE
    {{
        ?lens
            a                           bdb:Lens ;
            alivocab:operator           lensOp:union ;
            bdb:assertionMethod         ?method .
        ?method
            ?x                          ?y .
    }} ;

    ### DELETING THE METADATA
    DELETE {{ ?lens ?x ?y }}
    WHERE
    {{
        ?lens
            a                           bdb:Lens ;
            alivocab:operator           lensOp:union ;
            ?x                          ?y .
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DELETE {{ GRAPH ?graph {{  ?s ?p ?o  }} }}
    where
    {{
        GRAPH ?graph {{  ?s ?p ?o  }}
        Filter regex(str(?graph), 'union_', 'i')
    }}
    """.format(Ns.void, Ns.bdb, Ns.alivocab, Ns.lensOp)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING UNION...\nPLEASE WAIT FOR FEEDBACK",
            "\n======================================================="
            "=======================================================",)
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


#######################################################################################
# DROP INDIVIDUALS
#######################################################################################

def drop_linkset(graph, display=False, activated=True):

    queries = """
    #################################################################
    ### DELETE LINKSET NAMED GRAPHS AND METADATA                  ###
    #################################################################

    ### 1. DELETING GRAPHS's METADATA
    PREFIX void:    <{0}>
    PREFIX bdb:     <{1}>
    PREFIX link:    <{2}>

    DELETE {{ ?linktype ?x ?y }}
    where
    {{
      <{3}>
        void:linkPredicate  ?linktype .
      ?linktype
        ?x                  ?y
    }} ;

    ### 2. DELETING ASSERTION METADATA
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      <{3}>
        bdb:assertionMethod     ?assertionMethod .
      ?assertionMethod
        ?x                      ?y
    }} ;

    ### 3. DELETING JUSTIFICATION METADATA
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      <{3}>
        bdb:linksetJustification    ?linksetJustification .
      ?linksetJustification
        ?x                          ?y
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      <{3}>
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING THE META DATA
    DELETE {{ <{3}> ?x ?y . }}
    where
    {{
      <{3}>
               ?x   ?y
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DROP SILENT  GRAPH <{3}>

    """.format(Ns.void, Ns.bdb, Ns.alivocab, graph)

    if activated is False and display is True:
        print queries

    # print endpoint(queries, database_name, host)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING THE GRAPH <{}>... \nPLEASE WAIT FOR FEEDBACK.".format(graph),
            "\n======================================================="
            "======================================================="
        )
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""

#######################################################################################
# ABOUT RESEARCH QUESTIONS
#######################################################################################


def drop_all_research_questions(display=False, activated=False):

    query = """
    DELETE {GRAPH ?g {?s ?p ?o.} }
    WHERE
    {
        graph ?g
        {
          ?rq rdf:type	 <http://risis.eu/class/ResearchQuestion> .
          ?s ?p ?o.
        }
    }"""

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING ALL RESEARCH QUESTIONS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(query)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(query)
            print ""


def drop_research_question_lenses(research_uri, display=False, activated=False):

    query = """
    DELETE
    {{
        GRAPH <{0}>
        {{
            ?research_question ?p ?lens.
            ?lens a bdb:Lens.
        }}
    }}
    WHERE
    {{
        graph <{0}>
        {{
            ?research_question ?p ?lens.
        }}
        ?lens a bdb:Lens.
    }}""".format(research_uri, Ns.riclass)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING ALL LENSES REGISTERED UNDER [{}]..\nPLEASE WAIT FOR FEEDBACK.".format(research_uri),
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(query)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(query)
            print ""


def delete_aligned_linkset(research_uri, alignment_uri, display=False, activated=False):
    query = """
    DELETE
    {{
        graph <{0}>
        {{
            ?alignment ?alignmentProperty <{1}> .
        }}
    }}
    WHERE
    {{
        graph <{0}>
        {{
            ?alignment a  <http://risis.eu/class/AlignmentMapping> .
            ?alignment ?alignmentProperty <{1}> .
        }}
    }}
    """.format(research_uri, alignment_uri)

    if display is True:
        print query

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING THE SELECTED ALIGNMENT:\n[{}]\nPLEASE WAIT FOR FEEDBACK...".format(alignment_uri),
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(query)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(query)
        print ""


def delete_aligned_linksets(research_uri, display=False, activated=False):
    query = """
    DELETE
    {{
        GRAPH <{0}>
        {{
            ?alignment <{2}used>    ?linkset.
            ?alignment <{3}created> ?linkset.
        }}
    }}
    WHERE
    {{
        graph <{0}>
        {{
          ?alignment
            a  <{1}AlignmentMapping> ;
            (<{2}used>|<{3}created>) ?linkset.
        }}
    }}
    """.format(research_uri, Ns.riclass, Ns.prov, Ns.alivocab)

    if display is True:
        print query

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING ALL CREATED OR USED LINKSET REGISTERED FOR :\n[{}]\nPLEASE WAIT FOR FEEDBACK...".format(
                research_uri),
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        drops_response = endpoint(query)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(query)
        print ""

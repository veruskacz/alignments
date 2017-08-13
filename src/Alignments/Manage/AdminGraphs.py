import time
import xmltodict
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
from Alignments.Query import endpoint

error = 'The query was successfully executed but no feedback was returned'

PREFIX ="""
    ################################################################
    PREFIX bdb:         <{6}>
    PREFIX rdf:         <{5}>
    PREFIX linkset:     <{4}>
    PREFIX void:        <{3}>
    PREFIX alivocab:    <{0}>
    PREFIX tmpgraph:    <{2}>
    PREFIX prov:        <{1}>
""".format(Ns.alivocab, Ns.prov, Ns.tmpgraph, Ns.void, Ns.linkset, Ns.rdf, Ns.bdb)

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
            if len(drops_response[St.result]) == 0:
                return error
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
            if len(drops_response[St.result]) == 0:
                return error
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
            if len(drops_response[St.result]) == 0:
                return error
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def drop_a_lens(lens, display=False, activated=False):

    queries = """
    PREFIX void:    <{0}>
    PREFIX bdb:     <{1}>
    PREFIX link:    <{2}>

    ### 1. DELETING ASSERTION METHOD
    DELETE {{ ?assertionMethod ?x ?y }}
    where
    {{
      <{3}>
        a 							bdb:Lens ;
        bdb:assertionMethod 		?assertionMethod .
      ?assertionMethod ?x ?y .
    }} ;

    ### 2. DELETING JUSTIFICATION
    DELETE {{ ?linksetJustification ?x ?y }}
    where
    {{
      <{3}>
        a 							bdb:Lens ;
        bdb:linksetJustification 	?linksetJustification ;.
      ?linksetJustification ?x ?y .
    }} ;

    ### 3. DELETING LINK-TYPE
    DELETE {{ ?linkPredicate ?x ?y }}
    where
    {{
      <{3}>
        a 							bdb:Lens ;
        void:linkPredicate 			?linkPredicate .
      ?linkPredicate ?x ?y .
    }} ;

    ### 4. DELETING THE SINGLETON GRAPH
    DELETE {{ GRAPH ?singletonGraph {{ ?x ?y ?z }} }}
    where
    {{
      <{3}>
        a 							bdb:Lens ;
        link:singletonGraph 		?singletonGraph .
        GRAPH ?singletonGraph       {{ ?x ?y ?z }} .
    }} ;

    ### 5. DELETING THE METADATA
    DELETE {{ <{3}> ?x ?y }}
    where
    {{
      <{3}>
        a 							bdb:Lens ;
        ?x                          ?y.
    }} ;

    #################################################################
    ### DELETE LINKSET NAMED GRAPHS                              ###
    #################################################################
    DROP SILENT GRAPH <{3}>
    """.format(Ns.void, Ns.bdb, Ns.alivocab, lens)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING A LENS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        # print queries

        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            if len(drops_response[St.result]) == 0:
                return error
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
            if len(drops_response[St.result]) == 0:
                return error
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


#######################################################################################
# DROP INDIVIDUALS
#######################################################################################


def drop_linkset(graph, display=False, activated=False):

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
            "DROPPING THE LINKSET GRAPH <{}>... \nPLEASE WAIT FOR FEEDBACK.".format(graph),
            "\n======================================================="
            "======================================================="
        )
        drop_start = time.time()
        drops_response = endpoint(queries)
        drop_end = time.time()

        if drops_response[St.result] is not None:
            if len(drops_response[St.result]) == 0:
                return error
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(queries)
        print ""


def delete_linkset_rq(rq_uri, linkset_uri):

    # print "DELETE THE FILTERS AND DISCONNECT THE LINKSET"
    query1 = PREFIX + """
    # DELETE THE FILTERS
    DELETE
    {{
        GRAPH <{0}>
        {{
            <{0}>       alivocab:created    ?filter .
            ?filter     ?pred                ?obj .
        }}
    }}
    WHERE
    {{
        GRAPH <{0}>
        {{
            BIND(<{1}> AS ?linkset)
            <{0}>       alivocab:created    ?filter .
            ?filter     alivocab:appliesTo  ?linkset .
            ?filter     ?pred                ?obj .
        }}
    }};

    # 1 DISCONNECT THE LINKSET
    DELETE
    {{
        GRAPH <{0}>
        {{
             ?s         ?p                  ?linkset .
        }}
    }}
    WHERE
    {{

        BIND(<{1}> AS ?linkset) .
        GRAPH <{0}>
        {{
            ?s alivocab:created|prov:used ?linkset.
            ?s ?p ?linkset .
        }}

        FILTER NOT EXISTS
        {{
            GRAPH <{0}>
            {{
                ?view_lens alivocab:selected ?linkset.
            }}
        }}

        FILTER NOT EXISTS
        {{
            ?lens 	a 			?type;
                    void:target|void:subjectsTarget|void:objectsTarget  ?linkset.

            GRAPH <{0}>
            {{
               ?s3 alivocab:created|prov:used ?lens.
            }}
       }}
    }}""".format(rq_uri, linkset_uri)

    query2 = """DROP SILENT GRAPH <{0}> ;
    DROP SILENT GRAPH <{1}> ;

    # 2-B DELETE THE METADATA COMPLETELY IF IT'S NOT USED IN ANY RQ
    DELETE
    {{
        ?linkset ?p ?o .
        ?object ?pred ?obj .
    }}
    WHERE
    {{
        BIND(<{1}> AS ?linkset) .

        ?linkset    bdb:assertionMethod|bdb:linksetJustification    ?object .
        ?object     ?pred                                           ?obj .
        ?linkset    ?p                                              ?o .

        # FILTER NOT EXISTS
        # {{
        #     GRAPH ?rqg
        #     {{
        #         ?rqg a <http://risis.eu/class/ResearchQuestion> .
        #         ?sg ?pg ?linkset.
        #     }}
        # }}
    }}

    """.format(Ut.from_alignment2singleton(linkset_uri), linkset_uri)

    # print "DELETE THE BOTH METADATA"
    # query2 = PREFIX + """
    # # 2-A DELETE THE SINGLETON GRAPH IF IT'S NOT USED IN ANY RQ
    # DROP SILENT GRAPH <{}>
    # # DELETE
    # # {{
    # #     GRAPH       ?singletonGraph                 {{ ?x ?y ?z }} .
    # # }}
    # # WHERE
    # # {{
    # #     BIND(<{1}> AS ?linkset) .
    # #     ?linkset    alivocab:singletonGraph 		?singletonGraph .
    # #     GRAPH       ?singletonGraph                 {{ ?x ?y ?z }} .
    # #     FILTER NOT EXISTS
    # #     {{
    # #         GRAPH ?rqg
    # #         {{
    # #             ?rqg a <http://risis.eu/class/ResearchQuestion> .
    # #             ?sg ?pg ?linkset.
    # #         }}
    # #     }}
    # #     FILTER NOT EXISTS
    # #     {{
    # #         ?lens 	a 			?type;
    # #                 void:target|void:subjectsTarget|void:objectsTarget  ?linkset.
    # #     }}
    # # }}
    # ;
    # # 2-B DELETE THE METADATA COMPLETELY IF IT'S NOT USED IN ANY RQ
    # DELETE
    # {{
    #     ?linkset ?p ?o .
    #     ?object ?pred ?obj .
    # }}
    # WHERE
    # {{
    #     BIND(<{1}> AS ?linkset) .
    #
    #     ?linkset    bdb:assertionMethod|bdb:linksetJustification    ?object .
    #     ?object     ?pred                                           ?obj .
    #     ?linkset    ?p                                              ?o .
    #
    #     # FILTER NOT EXISTS
    #     # {{
    #     #     GRAPH ?rqg
    #     #     {{
    #     #         ?rqg a <http://risis.eu/class/ResearchQuestion> .
    #     #         ?sg ?pg ?linkset.
    #     #     }}
    #     # }}
    # }}
    # """.format(rq_uri, linkset_uri)



    # print "DELETING THE LINKSET ITSELF"
    # query3 = PREFIX + """
    # # 2-C DELETE THE LINKSET COMPLETELY IF IT'S NOT USED IN ANY RQ
    # DELETE
    # {{
    #     GRAPH   ?linkset    {{ ?sub ?pred ?obj . }}
    # }}
    # WHERE
    # {{
    #     BIND(<{1}> AS ?linkset) .
    #     GRAPH ?linkset
    #     {{
    #         ?sub    ?pred   ?obj .
    #     }}
    #     # FILTER NOT EXISTS
    #     # {{
    #     #     GRAPH ?rqg
    #     #     {{
    #     #         ?rqg a <http://risis.eu/class/ResearchQuestion> .
    #     #         ?sg ?pg ?linkset.
    #     #     }}
    #     # }}
    # }}
    #
    # """.format(rq_uri, linkset_uri)
    # print query
    return [query1, query2]


def delete_lens_rq(rq_uri, lens_uri):

    query = PREFIX + """
    # DELETE THE FILTERS
    DELETE
    {{
        GRAPH <{0}>
        {{
            <{0}>       alivocab:created    ?filter .
            ?filter     ?pred                ?obj .
        }}
    }}
    WHERE
    {{
        GRAPH <{0}>
        {{
            BIND(<{1}> AS ?lens)
            <{0}>       alivocab:created    ?filter .
            ?filter     alivocab:appliesTo  ?lens .
            ?filter     ?pred                ?obj .
        }}
    }};

    # 1 DISCONNECT THE LENS
    DELETE
    {{
        GRAPH <{0}>
        {{
             ?s         ?p                  ?lens.
        }}
    }}
    WHERE
    {{

        BIND(<{1}> AS ?lens) .
        GRAPH <{0}>
        {{
            ?s alivocab:created|prov:used ?lens.
            ?s ?p ?lens .
        }}

        FILTER NOT EXISTS
        {{
            GRAPH <{0}>
            {{
                ?view_lens alivocab:selected ?lens.
            }}
        }}

        FILTER NOT EXISTS
        {{
            ?anotherLens 	a 			?type;
                    void:target|void:subjectsTarget|void:objectsTarget ?lens.

            GRAPH <{0}>
            {{
               ?s3 alivocab:created|prov:used ?anotherLens.
            }}
       }}
    }}
     ;
    # 2-A DELETE THE SINGLETON GRAPH IF IT'S NOT USED IN ANY RQ
    DELETE
    {{
        GRAPH       ?singletonGraph                 {{ ?x ?y ?z }} .
    }}
    WHERE
    {{
        BIND(<{1}> AS ?lens) .
        ?lens    alivocab:singletonGraph 		?singletonGraph .
        GRAPH       ?singletonGraph                 {{ ?x ?y ?z }} .
        FILTER NOT EXISTS
        {{
            GRAPH ?rqg
            {{
                ?rqg a <http://risis.eu/class/ResearchQuestion> .
                ?sg ?pg ?lens.
            }}
        }}
         FILTER NOT EXISTS
        {{
            ?anotherLens 	a 			?type;
                    void:target|void:subjectsTarget|void:objectsTarget ?lens.
        }}
    }}
    ;
    # 2-B DELETE THE METADATA COMPLETELY IF IT'S NOT USED IN ANY RQ
    DELETE
    {{
        ?lens ?p ?o .
        ?object ?pred ?obj .
    }}
    WHERE
    {{
        BIND(<{1}> AS ?lens) .

        ?lens    bdb:assertionMethod|bdb:linksetJustification    ?object .
        ?object  ?pred                                           ?obj .
        ?lens    ?p                                              ?o .

        FILTER NOT EXISTS
        {{
            GRAPH ?rqg
            {{
                ?rqg a <http://risis.eu/class/ResearchQuestion> .
                ?sg ?pg ?lens.
            }}
        }}
    }}
    ;
    # 2-C DELETE THE LENS COMPLETELY IF IT'S NOT USED IN ANY RQ
    DELETE
    {{
        GRAPH   ?lens    {{ ?sub ?pred ?obj . }}
    }}
    WHERE
    {{
        BIND(<{1}> AS ?lens) .
        GRAPH ?lens
        {{
            ?sub    ?pred   ?obj .
        }}
        FILTER NOT EXISTS
        {{
            GRAPH ?rqg
            {{
                ?rqg a <http://risis.eu/class/ResearchQuestion> .
                ?sg ?pg ?lens.
            }}
        }}
    }}

    """.format(rq_uri, lens_uri)
    print query
    return query


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
            if len(drops_response[St.result]) == 0:
                return error
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(query)
            print ""


def drop_a_research_question(graph, display=False, activated=False):

    query = """DROP SILENT GRAPH <{}>""".format(graph)

    if activated is True:
        print "{}{}{}".format(
            "======================================================="
            "=======================================================\n",
            "DROPPING A RESEARCH QUESTIONS...\nPLEASE WAIT FOR FEEDBACK.",
            "\n======================================================="
            "=======================================================")
        drop_start = time.time()
        try:
            drops_response = endpoint(query)
        except Exception as error:
            print "\t>>> Query NOT executed'"
            print "\t>>>", error.message
            return error.message
        drop_end = time.time()

        if drops_response[St.result] is not None:
            if len(drops_response[St.result]) == 0:
                return 'The query was successfully executed but no feedback was returned'
            # print "drops_response", drops_response[St.result]
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print "\t>>> Query details  : {}\n".format(query)
            print ""
            return 'The query was successfully executed'
        else:
            return 'The query was not executed'


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
            if len(drops_response[St.result]) == 0:
                return error
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
            if len(drops_response[St.result]) == 0:
                return error
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
            if len(drops_response[St.result]) == 0:
                return error
            drops_doc = xmltodict.parse(drops_response[St.result])
            print "\t>>> Query executed : {:<14}".format(drops_doc['sparql']['boolean'])
            print "\t>>> Executed in    : {:<14} minute(s)".format(str((drop_end - drop_start) / 60))
            if display is True:
                print ">>> Query details  : {}\n".format(query)
        print ""

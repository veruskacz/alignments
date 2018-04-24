import logging
import time
import Alignments.Query as Qry
import Alignments.Utility as Ut
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.ErrorCodes as Ec
import Alignments.Server_Settings as Ss
import Alignments.GenericMetadata as Gn
import Alignments.Linksets.Linkset as Ls
import Alignments.UserActivities.UserRQ as Urq
from Alignments.Utility import update_specification
from Alignments.Linksets.Linkset import writelinkset
from Alignments.ConstraintClustering.DatasetsResourceClustering import linkset_from_clusters

DIRECTORY = Ss.settings[St.linkset_Exact_dir]
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
logger.addHandler(handler)


"""
SINGLE PREDICATE ALIGNMENT
    - THE NAME OF A LINKSET SHOULD BE FORMATTED AS [SRC DATASET]_[TARGET DATASET]_[SRC ALIGNS]_[MECHANISM]
    - spa_linksets ONY HANDLES THE EXACT STRING SIMILARITY MECHANISM
    - BECAUSE IDENTITY IS ABOUT MATCHING EXACT SUBJECT WITH THE SAME URI IDENTIFIER, THIS FUNCTION IS ALSO USED BY
      PLUGGING DIFFERENT INSERT QUERIES
    - THE "sameAsCount" VARIABLE HELPS CREATING TASK SPECIFIC PREDICATE BY APPENDING AN INTEGER TO THE PARENT PREDICATE.
      WHEN EVER THE "sameAsCount" VARIABLE IS NULL, AN ERROR-CODE 1 IS RETURNED
"""


def spa_linksets(specs, id=False, display=False, activated=False):

    # print "LINKSET FUNCTION ACTIVATED: {}".format(activated)
    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATED" \
              "\n======================================================" \
              "========================================================"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.error_code: 1, St.result: None}
    else:
        print "THE FUNCTION IS ACTIVATED"

    source = specs[St.source]
    target = specs[St.target]

    """
    # CHECK WHETHER A METADATA DESCRIBING THIS LINKSET EXIST
    """
    # THE NAME OF A LINKSET SHOULD BE FORMATTED AS FOLLOW:
    #   [SRC DATASET]_[TARGET DATASET]_[SRC ALIGNS]_[MECHANISM]
    if St.linkset not in specs:
        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_name(specs)

    # This function is designed for EXACT NAME SIMILARITY RUN AS SPARQL QUERIES
    # if True:
    try:
    # if True:
        if activated is True:
            # print "NAME: " + specs[St.linkset]
            # CHECK WHETHER OR NOT THE LINKSET WAS ALREADY CREATED
            # print Ls.linkset_info(specs, specs[St.sameAsCount])

            if id is False:
                check = Ls.run_checks(specs, check_type="linkset")
            else:
                check = Ls.run_checks_id(specs)

            if check[St.result] != "GOOD TO GO":
                return check

            # print "NAME: " + specs[St.linkset]

            # THE LINKSET DOES NOT EXIT, LETS CREATE IT NOW
            print Ls.linkset_info(specs, specs[St.sameAsCount])

            # Generating insert quarries
            insertqueries = specs[St.linkset_insert_queries]

            # LINKSET insert Query
            specs[St.insert_query] = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
            # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]

            ########################################################################
            print """ 1. SAFETY GRAPH DROPS                                      """
            ########################################################################
            print insertqueries[0]
            Qry.boolean_endpoint_response(insertqueries[0])

            ########################################################################
            print """ 2.1 SOURCE TEMPORARY GRAPHS                                """
            ########################################################################
            ls_start = time.time()
            print insertqueries[1]
            Qry.boolean_endpoint_response(insertqueries[1])

            ########################################################################
            print """ 2.2 TARGET TEMPORARY GRAPHS                                """
            ########################################################################
            print insertqueries[2]
            Qry.boolean_endpoint_response(insertqueries[2])

            ########################################################################
            print """ 2.3 TEMPORARY MATCH GRAPH                                  """
            ########################################################################
            print insertqueries[3]
            Qry.boolean_endpoint_response(insertqueries[3])

            ########################################################################
            print """ 3. LINKSET & METADATA                                      """
            ########################################################################
            print insertqueries[4]
            Qry.boolean_endpoint_response(insertqueries[4])

            ########################################################################
            print """ 4. DROPPING TEMPORARY GRAPHS                               """
            ########################################################################
            print insertqueries[5]
            Qry.boolean_endpoint_response(insertqueries[5])

            ########################################################################
            print """ 5. GENERATING LINKSET METADATA                             """
            ########################################################################
            metadata = Gn.linkset_metadata(specs)
            # print metadata
            ls_end = time.time()
            diff = ls_end - ls_start
            print ">>> Executed in    : {:<14} minute(s) []".format(str(diff/ 60), diff)

            # NO POINT TO CREATE ANY FILE WHEN NO TRIPLE WAS INSERTED
            if int(specs[St.triples]) > 0:

                Qry.boolean_endpoint_response(metadata)

                ########################################################################
                print """ 6. WRITING TO FILE                                         """
                ########################################################################
                src = [source[St.graph_name], "", source[St.entity_ns]]
                trg = [target[St.graph_name], "", target[St.entity_ns]]

                print "\t>>> WRITING TO FILE"
                # linkset_path = "D:\datasets\Linksets\ExactName"
                linkset_path = DIRECTORY
                writelinkset(src, trg, specs[St.linkset_name], linkset_path, metadata)
                server_message = "Linksets created as: {}".format(specs[St.linkset])
                message = "The linkset was created as [{}] with {} triples found!".format(
                    specs[St.linkset], specs[St.triples])
                print "\t", server_message
                print "\t*** JOB DONE! ***"

                if display is True:
                    # Generating insert quarries
                    insertqueries = spa_linkset_ess_query(specs)
                    # LINKSET insert Query
                    specs[St.insert_query] = "{}\n{}\n{}".format(insertqueries[1], insertqueries[2], insertqueries[3])
                    # print insertqueries[0], '\n', insertqueries[1], '\n', insertqueries[2], '\n', insertqueries[3]
                    metadata = Gn.linkset_metadata(specs)
                    print metadata

                return {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

            else:
                return {St.message: Ec.ERROR_CODE_4.replace('\n', "<br/>"), St.error_code: 4, St.result: None}

    except Exception as err:
        # logger.warning(err)
        print "ERROR IN SPA_LINKSET", err
        return {St.message: Ec.ERROR_CODE_4.replace('\n', "<br/>"), St.error_code: 4, St.result: None}


########################################################################################
# SINGLE PREDICATE ALIGNMENT
########################################################################################


def spa_linkset_ess_query(specs):
    # Single Predicate Alignment with Exact String Similarity
    source = specs[St.source]
    target = specs[St.target]

    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        "##################################################################",
        "### Linking {{{}}} to {{{}}} based on exact name".format(source[St.graph_name], target[St.graph_name]),
        "##################################################################",
        "prefix dataset:    <{}>".format(Ns.dataset),
        "prefix linkset:    <{}>".format(Ns.linkset),
        "prefix singleton:  <{}>".format(Ns.singletons),
        "prefix alivocab:   <{}>".format(Ns.alivocab),
        "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
        "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))
    '''
        DROPPING GRAPHS
    '''
    drop_tmp = "DROP SILENT GRAPH tmpgraph:load"
    drop_tmp00 = "DROP SILENT GRAPH tmpgraph:load00"
    drop_tmp01 = "DROP SILENT GRAPH tmpgraph:load01"
    # drop_ls = "DROP SILENT GRAPH linkset:{}_{}_ExactName".format(src_dataset_name, trg_dataset_name)
    # drop_metadata = "DROP SILENT GRAPH lsMetadata:{}_{}_ExactName_metadata".format(src_dataset_name, trg_dataset_name)

    drop_ls = "DROP SILENT GRAPH linkset:{}".format(specs[St.linkset_name])
    drop_metadata = "DROP SILENT GRAPH singleton:{}".format(specs[St.linkset_name])

    '''
        LOADING SOURCE TO TEMPORARY GRAPH tmpgraph:load00
    '''

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns]\
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns]\
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    # REPLACE RDF TYPE "a" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in source and source[St.rdf_predicate] is not None:
        src_rdf_pred = source[St.rdf_predicate]\
            if Ls.nt_format(source[St.rdf_predicate]) else "<{}>".format(source[St.rdf_predicate])
    else:
        src_rdf_pred = "a"

    if St.rdf_predicate in target and target[St.rdf_predicate] is not None:
        trg_rdf_pred = target[St.rdf_predicate] \
            if Ls.nt_format(target[St.rdf_predicate]) else "<{}>".format(target[St.rdf_predicate])
    else:
        trg_rdf_pred = "a"

    load_temp00 = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load00",
               "\t  {",
               "\t    ?source alivocab:hasProperty ?label .",
               "\t  }",
               "\t}",

               "\tWHERE",
               "\t{",
               "\t  ### Selecting source data instances based on name",
               "\t  GRAPH <{}>".format(source[St.graph]),
               "\t  {",
               "\t    ?source {} <{}> .".format(src_rdf_pred, source[St.entity_datatype]),
               "\t    ?source {} ?aLabel .".format(src_aligns),
               "\t    BIND(lcase(str(?aLabel)) as ?label)",
               "\t  }",
               "\t}")

    '''
        LOADING TARGET TO TEMPORARY GRAPH tmpgraph:load01
    '''
    load_temp01 = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load01",
               "\t  {",
               "\t    ?target alivocab:hasProperty  ?label .",
               "\t  }",
               "\t}",

               "\tWHERE",
               "\t{",
               "\t  ### Selecting target data instances based on exact name",
               "\t  graph <{}>".format(target[St.graph]),
               "\t  {",
               "\t    ?target {} <{}> .".format(trg_rdf_pred, target[St.entity_datatype]),
               "\t    ?target {}  ?bLabel .".format(trg_aligns),
               "\t    BIND(lcase(str(?bLabel)) as ?label)",
               "\t  }",
               "\t}")

    '''
        LOADING CORRESPONDENCE TO TEMPORARY GRAPH tmpgraph:load
    '''
    load_temp = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH tmpgraph:load",
               "\t  {",
               "\t    ?source tmpvocab:exactName ?target ;",
               "\t            tmpvocab:evidence  ?label .",
               "\t  }",
               "\t}",
               # Load
               "\tWHERE",
               "\t{",
               "\t  ### Selecting source data instances based on name",
               "\t  GRAPH tmpgraph:load00",
               "\t  {",
               "\t    ?source alivocab:hasProperty ?label .",
               "\t  }",

               "\t  ### Selecting target data instances based on exact name",
               "\t  graph tmpgraph:load01",
               "\t  {",
               "\t    ?target alivocab:hasProperty  ?label .",
               "\t  }",

               "\t}", )

    '''
        CREATING THE LINKSET & METADATA GRAPHS lsMetadata
    '''
    load_linkset = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}" \
                   "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}". \
        format("\tINSERT",
               "\t{",
               "\t  GRAPH linkset:{}".format(specs[St.linkset_name]),
               "\t  {",
               "\t    ### Correspondence triple with singleton",
               "\t    ?source ?singPre ?target.",
               "\t  }",

               "\t  GRAPH singleton:{}".format(specs[St.linkset_name]),
               "\t  {",
               "\t    ### Singleton metadata",
               "\t    ?singPre rdf:singletonPropertyOf     alivocab:exactStrSim{} ;".format(specs[St.sameAsCount]),
               "\t             alivocab:hasEvidence        ?label .",
               "\t  }",

               "\t}",
               "\tWHERE",
               "\t{",
               "\t  ### Selecting from tmpgraph:load",
               "\t  GRAPH tmpgraph:load",
               "\t  {",
               "\t    ?source tmpvocab:exactName ?target ;",
               "\t            tmpvocab:evidence  ?label .",
               "\t            ",
               "\t    ### Create A SINGLETON URI",
               "\t    BIND( replace(\"{}{}{}_#\",\"#\",".format(
                   Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount]),
               "\t        STRAFTER(str(UUID()),\"uuid:\")) as ?pre )",
               "\t    BIND(iri(?pre) as ?singPre)",
               "\t  }",
               "\t}")

    '''
        PUTTING IT ALL TOGETHER
    '''
    query01 = "{}\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n{} ;\n\n{}\n\t{}".format(
        prefix,
        "### 1.0 DROP temporary graph",
        drop_tmp,
        "### 1.1 DROP SOURCE temporary graph 00",
        drop_tmp00,
        "### 1.2 DROP TARGET temporary graph 01",
        drop_tmp01,
        "### 1.3 DROP LINKSET graph",
        drop_ls,
        "### 1.4 DROP METADATA graph",
        drop_metadata
    )

    query02 = "{}\n\n{}\n{} ;\n\n{}\n{} ;\n\n{}\n{} ".format(
        prefix,
        "### 2.0 INSERT SOURCE into tmpgraph:load00",
        load_temp00,
        "### 2.1 INSERT TARGET into tmpgraph:load01",
        load_temp01,
        "### 2.3 INSERT CORRESPONDENCE [match] into tmpgraph:load",
        load_temp,
    )

    query03 = "{}\n\n{}\n{}".format(
        prefix,
        "### 3.0 CREATING AND LOADING THE LINKSET AND ITS METADATA",
        load_linkset,
    )

    query04 = "{}\n\n{}\n\t{} ;\n\t{} ;\n\t{}".format(
        prefix,
        "### 4.0 DROP temporary graphs",
        drop_tmp00,
        drop_tmp01,
        drop_tmp
    )
    # print query01, query02, query03, query04
    queries = [query01, query02, query03, query04]
    return queries


# THIS FUNCTION REPLACES spa_linkset_ess_query AS IT ADDS THE POSSIBILITY TO
# REDUCE THE SOURCE OR TARGET'S NUMBER OF INSTANCE TO BE MATCHED AGAINST
def extract_query(specs, is_source):

    # UPDATE THE SPECS OF SOURCE AND TARGETS
    if is_source is True:
        info = specs[St.source]
        load = "_1"
    else:
        info = specs[St.target]
        load = "_2"

    # REPLACE RDF TYPE "a" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in info and info[St.rdf_predicate] is not None:
        rdf_pred = info[St.rdf_predicate] \
            if Ls.nt_format(info[St.rdf_predicate]) else "<{}>".format(info[St.rdf_predicate])
    else:
        rdf_pred = "a"

    # FORMATTING THE ALIGNS PROPERTY
    aligns = info[St.aligns] \
        if Ls.nt_format(info[St.aligns]) else "<{}>".format(info[St.aligns])

    name = info[St.graph_name]
    uri = info[St.graph]

    # ADD THE REDUCER IF SET
    if St.reducer not in info:
        reducer_comment = "#"
        reducer = ""
    else:
        reducer_comment = ""
        reducer = info[St.reducer]

    # EXTRACTION QUERY
    query = """
    INSERT
    {{
        GRAPH <{0}load{8}>
        {{
            ?{5}  alivocab:hasProperty  ?trimmed .
        }}
    }}
    WHERE
    {{
        GRAPH <{1}>
        {{
            ?{5}  {2}  <{7}> .
            ?{5}  {3}  ?object .

            # LOWER CASE OF THE VALUE
            BIND(lcase(str(?object)) as ?label)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?label, ?regexp, '$1$2') AS ?trimmed)
        }}

        {6}FILTER NOT EXISTS
        {6}{{
        {6}    GRAPH <{4}>
        {6}    {{
        {6}        {{ ?{5}   ?pred   ?obj . }}
        {6}        UNION
        {6}        {{ ?obj   ?pred   ?{5}. }}
        {6}    }}
        {6}}}
    }} ;
    """.format(Ns.tmpgraph, uri, rdf_pred, aligns,
               reducer, name, reducer_comment, info[St.entity_datatype], load)
    return query


# STRING-BASED -> THIS COMPUTES TWO QUERIES: MATCHED AND INSERT MATCHED
def match_query(specs):

    is_de_duplication = (specs[St.source][St.graph] == specs[St.target][St.graph]) and \
                        (specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype])

    operator = "<" if specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype] else "!="

    comment = "" if is_de_duplication is True else "#"
    number_of_load = '1' if is_de_duplication is True else "2"

    match = """
    INSERT
    {{
        GRAPH tmpgraph:load_3
        {{
            ?{0}_1  tmpvocab:exactName  ?{1}_2 .
            ?{0}_1  tmpvocab:evidence   ?label .
        }}
    }}
    WHERE
    {{
        GRAPH tmpgraph:load_1
        {{
            ?{0}_1 ?hasProperty ?label .
        }}
        GRAPH tmpgraph:load_{3}
        {{
            ?{1}_2 ?hasProperty ?label .
        }}

        # DO NOT INCLUDE SAME URIs AND INVERSE DIRECTION DUPLICATES
        {2}FILTER( STR(?{0}_1) {4} STR(?{0}_2) )
    }}
    """.format(
        specs[St.source][St.graph_name], specs[St.target][St.graph_name],
        comment, number_of_load, operator)

    linkset = """
    INSERT
    {{
        GRAPH linkset:{0}
        {{
            ### Correspondence triple with singleton
            ?source ?singPre ?target.
        }}
        GRAPH singleton:{0}
        {{
            ### Singleton metadata##
            ?singPre rdf:singletonPropertyOf     alivocab:exactStrSim{1} .
            ?singPre alivocab:hasStrength        1 .
            ?singPre alivocab:hasEvidence        ?label .
        }}
    }}
    WHERE
    {{
        ### Selecting from tmpgraph:load_3
        GRAPH tmpgraph:load_3
        {{
            ?source tmpvocab:exactName ?target .
            ?source tmpvocab:evidence  ?label .
            ### Create A SINGLETON URI
            BIND( replace(\"{2}{3}{4}_#\",\"#\", STRAFTER(str(UUID()),\"uuid:\")) as ?pre )
            BIND(iri(?pre) as ?singPre)
        }}
    }} ;
    """.format(specs[St.linkset_name], specs[St.sameAsCount],
               Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount])

    # query = match + linkset
    return [match, linkset]


# NUMERIC-BASED -> THIS COMPUTES TWO QUERIES: MATCHED AND INSERT MATCHED
def match_numeric_query(specs):

    is_de_duplication = (specs[St.source][St.graph] == specs[St.target][St.graph]) \
                        and (specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype])

    number_of_load = '1' if is_de_duplication is True else "2"

    # PLAIN NUMBER CHECK
    delta_check = "BIND(ABS(xsd:decimal(?x) - xsd:decimal(?x)) AS ?DELTA)"

    # DATE CHECK
    if specs[St.numeric_approx_type].lower() == "date":
        delta_check = "BIND( (YEAR(xsd:datetime(STR(?x))) - YEAR(xsd:datetime(STR(?y))) ) as ?DELTA )"

    match = """
    INSERT
    {{
        GRAPH tmpgraph:load_3
        {{
            ?{0}_1  tmpvocab:exactName  ?{1}_2 .
            ?{0}_1  tmpvocab:evidence   ?DELTA .
        }}
    }}
    WHERE
    {{

        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{0}_1 ?pred  ?{1}_2 .
        }}

        GRAPH tmpgraph:load_1
        {{
            ?{0}_1 ?hasProperty ?x .
        }}
        GRAPH tmpgraph:load_{4}
        {{
            ?{1}_2 ?hasProperty ?y .
        }}

        # DELTA APPROX CHECK
        {3}

        FILTER( ABS(?DELTA) <= {2} )
    }}
    """.format(specs[St.source][St.graph_name], specs[St.target][St.graph_name], specs[St.delta], delta_check,
               number_of_load, specs[St.linkset])

    linkset = """
    INSERT
    {{
        GRAPH linkset:{0}
        {{
            ### Correspondence triple
            ?source ?singPre ?target.
        }}
        GRAPH singleton:{0}
        {{
            ### Singleton metadata
            ?singPre rdf:singletonPropertyOf  alivocab:exactStrSim{1} .
            ?singPre alivocab:hasEvidence     ?label .
        }}
    }}
    WHERE
    {{
        ### Selecting from tmpgraph:load_3
        GRAPH tmpgraph:load_3
        {{
            ?source tmpvocab:exactName ?target .
            ?source tmpvocab:evidence  ?label .
            ### Create A SINGLETON URI
            BIND( replace(\"{2}{3}{4}_#\",\"#\", STRAFTER(str(UUID()),\"uuid:\")) as ?pre )
            BIND(iri(?pre) as ?singPre)
        }}
    }} ;
    """.format(specs[St.linkset_name], specs[St.sameAsCount],
               Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount])

    # query = match + linkset
    return [match, linkset]


def insert_query_reduce(specs, match_numeric=False):

    is_de_duplication = (specs[St.source][St.graph] == specs[St.target][St.graph]) and \
                        (specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype])

    prefix = """
    prefix dataset:    <{}>
    prefix linkset:    <{}>
    prefix singleton:  <{}>
    prefix alivocab:   <{}>
    prefix tmpgraph:   <{}>
    prefix tmpvocab:   <{}>
    """.format(Ns.dataset, Ns.linkset, Ns.singletons, Ns.alivocab, Ns.tmpgraph, Ns.tmpvocab)

    drop_q1 = """
    DROP SILENT GRAPH <{0}load_1> ;
    DROP SILENT GRAPH <{0}load_2> ;
    DROP SILENT GRAPH <{0}load_3> ;
    DROP SILENT GRAPH <{1}> ;
    DROP SILENT GRAPH <{2}{3}>
    """.format(Ns.tmpgraph, specs[St.linkset], Ns.singletons, specs[St.linkset_name])

    drop_q2 = """
    DROP SILENT GRAPH <{0}load_1> ;
    DROP SILENT GRAPH <{0}load_2> ;
    DROP SILENT GRAPH <{0}load_3>
    """.format(Ns.tmpgraph)

    source_extract = extract_query(specs, is_source=True)
    target_extract = "" if is_de_duplication is True else extract_query(specs, is_source=False)

    if match_numeric is False:
        match = match_query(specs)
    else:
        match = match_numeric_query(specs)

    query_1 = drop_q1
    query_2 = prefix + source_extract
    query_3 = prefix + target_extract
    query_4 = prefix + match[0]
    query_5 = prefix + match[1]
    query_6 = drop_q2
    # print query_1
    # print query_2
    # print query_3
    # print query_4
    return [query_1, query_2, query_3, query_4, query_5, query_6]


def specs_2_linkset(specs, match_numeric=False, display=False, activated=False):

    # if activated is True:
    heading = "======================================================" \
              "========================================================" \
              "\nEXECUTING LINKSET SPECS"

    print heading
    # inserted_mapping = None
    # inserted_linkset = None

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT BEFORE YOU DO ANYTHING
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    if specs[St.sameAsCount]:

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_name(specs)

        # SET THE INSERT QUERY
        # specs[St.linkset_insert_queries] = spa_linkset_ess_query(specs)
        specs[St.linkset_insert_queries] = insert_query_reduce(specs, match_numeric)
        # GENERATE THE LINKSET
        # print "specs_2_linkset FUNCTION ACTIVATED: {}".format(activated)
        inserted_linkset = spa_linksets(specs, display=display, activated=activated)

        if activated is True:

            # REGISTER THE ALIGNMENT
            if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
                Urq.register_alignment_mapping(specs, created=False)
            else:
                Urq.register_alignment_mapping(specs, created=True)

        # SPA_LINKSET returns
        # {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}
        return inserted_linkset

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


def specs_2_linkset_num_approx(specs,  match_numeric=False, display=False, activated=False):

    # if activated is True:
    heading = "======================================================" \
              "========================================================" \
              "\nEXECUTING LINKSET SPECS"

    print heading
    # inserted_mapping = None
    # inserted_linkset = None

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT BEFORE YOU DO ANYTHING
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    if specs[St.sameAsCount]:

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_name(specs)

        # SET THE INSERT QUERY
        # specs[St.linkset_insert_queries] = spa_linkset_ess_query(specs)
        specs[St.linkset_insert_queries] = insert_query_reduce(specs, match_numeric)

        # GENERATE THE LINKSET
        # print "specs_2_linkset FUNCTION ACTIVATED: {}".format(activated)
        inserted_linkset = spa_linksets(specs, display=display, activated=activated)

        if activated is True:

            # REGISTER THE ALIGNMENT
            if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
                Urq.register_alignment_mapping(specs, created=False)
            else:
                Urq.register_alignment_mapping(specs, created=True)

        return inserted_linkset

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


########################################################################################
# SINGLE PREDICATE ALIGNMENT IDENTITY
# ALIGNING SUBJECTS FROM DIFFERENT GRAPHS THAT HAVE THE SAME RESOURCE URI IDENTIFIER
########################################################################################


def spa_linkset_identity_query(specs):
    # Single Predicate Alignment with Exact String Similarity

    source = specs[St.source]
    target = specs[St.target]

    src_aligns = source[St.aligns]\
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns]\
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        "##################################################################",
        "### Linking {{{}}} to {{{}}} based on exact name".format(source[St.graph_name], target[St.graph_name]),
        "##################################################################",
        "prefix dataset:    <{}>".format(Ns.dataset),
        "prefix linkset:    <{}>".format(Ns.linkset),
        "prefix singleton:  <{}>".format(Ns.singletons),
        "prefix alivocab:   <{}>".format(Ns.alivocab),
        "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
        "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))

    ''' DROPPING GRAPHS '''
    drop_tmp = "DROP SILENT GRAPH tmpgraph:load"
    drop_tmp00 = "DROP SILENT GRAPH tmpgraph:load00"
    drop_tmp01 = "DROP SILENT GRAPH tmpgraph:load01"

    drop_ls = "DROP SILENT GRAPH linkset:{}".format(specs[St.linkset_name])
    drop_metadata = "DROP SILENT GRAPH singleton:{}".format(specs[St.linkset_name])

    ''' LOADING SOURCE TO TEMPORARY GRAPH tmpgraph:load00 '''
    load_temp00 = """
    INSERT
    {{
        GRAPH tmpgraph:load00
        {{
            ?source {0} <{1}> .
        }}
    }}
    WHERE
    {{
        ### Selecting source data instances based on name
        GRAPH <{2}>
        {{
            ?source {0} <{1}> .
        }}
    }}""".format(src_aligns, source[St.entity_datatype], source[St.graph])

    ''' LOADING TARGET TO TEMPORARY GRAPH tmpgraph:load01 '''
    load_temp01 = """
    INSERT
    {{
       GRAPH tmpgraph:load01
       {{
            ?target {0} <{1}> .
       }}
    }}
    WHERE
    {{
       ### Selecting target data instances based on name
       GRAPH <{2}> {{ ?target {0} <{1}> . }}
    }}""".format(trg_aligns, target[St.entity_datatype], target[St.graph])

    ''' LOADING CORRESPONDENCE TO TEMPORARY GRAPH tmpgraph:load '''
    load_temp = """
    INSERT
    {{
        GRAPH tmpgraph:load
        {{
            ?subject tmpvocab:identical ?subject ;
                     tmpvocab:evidence  "Identical resource URI ." .
        }}
    }}
    WHERE
    {{
        GRAPH tmpgraph:load00 {{ ?subject {} <{}> . }}
        GRAPH tmpgraph:load01 {{ ?subject {} <{}> . }}
    }}""".format(src_aligns, source[St.entity_datatype],
                 trg_aligns, target[St.entity_datatype])

    ''' CREATING THE LINKSET & METADATA GRAPHS lsMetadata '''
    load_linkset = """
        INSERT
        {{
            GRAPH linkset:{0}
            {{
                ### Correspondence triple with singleton
                ?source ?singPre ?target .
            }}

            GRAPH singleton:{0}
            {{
                ### ### Singleton metadata
                ?singPre
                    rdf:singletonPropertyOf     alivocab:exactStrSim{1} ;
                    alivocab:hasEvidence        ?label .
            }}
        }}
        WHERE
        {{
            ### Selecting from tmpgraph:load
            GRAPH tmpgraph:load
            {{
                ?source
                    tmpvocab:identical ?target ;
                    tmpvocab:evidence  ?label .

                ### Create A SINGLETON URI"
                BIND( replace("{2}{3}{4}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
                BIND( iri(?pre) as ?singPre )
            }}
        }}""".format(specs[St.linkset_name], specs[St.sameAsCount],
                     Ns.alivocab, specs[St.mechanism],  specs[St.sameAsCount])

    '''
        PUTTING IT ALL TOGETHER
    '''
    query01 = "{}\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n\t{} ;\n\n{}\n{} ;\n\n{}\n\t{}".format(
        prefix,
        "### 1.0 DROP temporary graph",
        drop_tmp,
        "### 1.1 DROP SOURCE temporary graph 00",
        drop_tmp00,
        "### 1.2 DROP TARGET temporary graph 01",
        drop_tmp01,
        "### 1.3 DROP LINKSET graph",
        drop_ls,
        "### 1.4 DROP METADATA graph",
        drop_metadata
    )

    query02 = "{}\n\n{}\n{} ;\n\n{}\n{} ;\n\n{}\n{} ".format(
        prefix,
        "### 2.0 INSERT SOURCE into tmpgraph:load00",
        load_temp00,
        "### 2.1 INSERT TARGET into tmpgraph:load01",
        load_temp01,
        "### 2.3 INSERT CORRESPONDENCE [match] into tmpgraph:load",
        load_temp,
    )

    query03 = "{}\n\n{}\n{}".format(
        prefix,
        "### 3.0 CREATING AND LOADING THE LINKSET AND ITS METADATA",
        load_linkset,
    )

    query04 = "{}\n\n{}\n\t{} ;\n\t{} ;\n\t{}".format(
        prefix,
        "### 4.0 DROP temporary graphs",
        drop_tmp00,
        drop_tmp01,
        drop_tmp
    )

    queries = [query01, query02, query03, query04]
    # print query01
    # print query02
    # print query03

    return queries


def specs_2_linkset_id(specs, display=False, activated=False):

    print "======================================================" \
          "========================================================" \
          "\nEXECUTING LINKSET SPECS"

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    # UPDATE THE QUERY THAT IS GOING TO BE EXECUTED
    if specs[St.sameAsCount]:

        specs[St.source][St.aligns] = "{}type".format(Ns.rdf)
        specs[St.target][St.aligns] = "{}type".format(Ns.rdf)

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_identity_name(specs)

        # SET THE INSERT QUERY
        specs[St.linkset_insert_queries] = spa_linkset_identity_query(specs)
        # print specs[St.linkset_insert_queries]

        # GENERATE THE LINKSET
        inserted_linkset = spa_linksets(specs, id=True, display=display, activated=activated)

        # REGISTER THE ALIGNMENT
        if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
            Urq.register_alignment_mapping(specs, created=False)
        else:
            Urq.register_alignment_mapping(specs, created=True)

        # SPA_LINKSET returns
        # {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}
        return inserted_linkset

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


########################################################################################
# ALIGNING SUBJECTS USING AN INTERMEDIATE DATASET
########################################################################################

# DEPRECATED (TODO TO DELETE)
def spa_linkset_intermediate_query_2(specs):

    source = specs[St.source]
    target = specs[St.target]

    # REPLACE RDF TYPE "a" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in source and source[St.rdf_predicate] is not None:
        src_rdf_pred = source[St.rdf_predicate] \
            if Ls.nt_format(source[St.rdf_predicate]) else "<{}>".format(source[St.rdf_predicate])
    else:
        src_rdf_pred = "a"

    if St.rdf_predicate in target and target[St.rdf_predicate] is not None:
        trg_rdf_pred = target[St.rdf_predicate] \
            if Ls.nt_format(target[St.rdf_predicate]) else "<{}>".format(target[St.rdf_predicate])
    else:
        trg_rdf_pred = "a"

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = specs[St.source][St.graph_name]
    src_uri = specs[St.source][St.graph]
    # src_aligns = specs[St.source][St.aligns]

    trg_name = specs[St.target][St.graph_name]
    trg_uri = specs[St.target][St.graph]
    # trg_aligns = specs[St.target][St.aligns]

    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        "##################################################################",
        "### Linking {{{}}} to {{{}}} based on exact name".format(source[St.graph_name], target[St.graph_name]),
        "##################################################################",
        "prefix dataset:    <{}>".format(Ns.dataset),
        "prefix linkset:    <{}>".format(Ns.linkset),
        "prefix singleton:  <{}>".format(Ns.singletons),
        "prefix alivocab:   <{}>".format(Ns.alivocab),
        "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
        "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))

    query01 = """
    DROP SILENT GRAPH <{0}load00> ;
    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02> ;
    DROP SILENT GRAPH <{1}{2}>
    """.format(Ns.tmpgraph, Ns.singletons, specs[St.linkset_name])

    query02 = prefix + """
    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH <{0}load00>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1}_1 <{8}relatesTo1> ?src_value .
        }}
        GRAPH <{0}load01>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3}_2 <{8}relatesTo3> ?trg_value .
        }}
    }}
    WHERE
    {{
        ### SOURCE DATASET
        graph <{6}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1}_1 {10} <{12}> .
            ?{1}_1 {2} ?value_1 .
            bind (lcase(str(?value_1)) as ?src_value)
        }}
        ### TARGET DATASET
        graph <{7}>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3}_2 {11} <{13}> .
            ?{3}_2 {4} ?value_2 .
            bind (lcase(str(?value_2)) as ?trg_value)
        }}
    }} ;

    ### 2. FINDING CANDIDATE MATCH
    INSERT
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1}_1 <{8}relatesTo> ?{3}_2 .
        }}
    }}
    WHERE
    {{
        ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
        GRAPH <{0}load00>
        {{
            ?{1}_1 <{8}relatesTo1> ?src_value .
        }}
        GRAPH <{0}load01>
        {{
            ?{3}_2 <{8}relatesTo3> ?trg_value .
        }}
        ### INTERMEDIATE DATASET VIA URI
        graph <{9}>
        {{
            ?intermediate_uri
                ?intPred_1 ?value_3 ;
                ?intPred_2 ?value_4 .
            bind (lcase(?value_3) as ?src_value)
            bind (lcase(?value_4) as ?trg_value)
        }}
    }}
    """.format(
        # 0          1         2           3         4
        Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
        # 5                6        7        8            9
        specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
        # 10          11            12                          13
        src_rdf_pred, trg_rdf_pred, source[St.entity_datatype], target[St.entity_datatype]
    )

    query03 = prefix + """
    ### 3. CREATING THE CORRESPONDENCES
    INSERT
    {{
        GRAPH <{5}>
        {{
            ?{1}_1 ?newSingletons  ?{3}_2 .
        }}
        ### SINGLETONS' METADATA
        GRAPH <{10}{11}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{8}{9} ;
                alivocab:hasStrength        1 ;
                alivocab:hasEvidence        ?evidence .
        }}
    }}
    WHERE
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1}_1 <{6}relatesTo> ?{3}_2 .
             bind( iri(replace("{7}{8}{9}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}
        {{
            SELECT ?{1}_1 ?{3}_2 ?evidence
            {{
                ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
                GRAPH <{0}load00>
                {{
                    ?{1}_1 <{6}relatesTo1> ?src_value .
                }}
                GRAPH <{0}load01>
                {{
                    ?{3}_2 <{6}relatesTo3> ?trg_value .
                }}
                BIND(concat("[", ?src_value, "] aligns with [", ?trg_value, "]") AS ?evidence)
            }}
        }}
    }}
    """.format(
        # 0          1         2           3         4           5                  6
        Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns, specs[St.linkset], Ns.tmpvocab,
        # 7          8                    9                      10             11
        Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount], Ns.singletons, specs[St.linkset_name],
    )
    # insert = """
    # PREFIX alivocab:    <{16}>
    # PREFIX prov:        <{17}>
    #
    # DROP SILENT GRAPH <{0}load01> ;
    # DROP SILENT GRAPH <{0}load02> ;
    # DROP SILENT GRAPH <{10}> ;
    # DROP SILENT GRAPH <{14}{15}> ;
    #
    # ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    # INSERT
    # {{
    #     GRAPH <{0}load01>
    #     {{
    #         ### SOURCE DATASET AND ITS ALIGNED PREDICATE
    #         ?{1} {2} ?src_value .
    #         ### TARGET DATASET AND ITS ALIGNED PREDICATE
    #         ?{3} {4} ?trg_value .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE DATASET
    #     graph <{6}>
    #     {{
    #         ### SOURCE DATASET AND ITS ALIGNED PREDICATE
    #         ?{1} {2} ?value_1 .
    #         bind (lcase(str(?value_1)) as ?src_value)
    #     }}
    #     ### TARGET DATASET
    #     graph <{7}>
    #     {{
    #         ### TARGET DATASET AND ITS ALIGNED PREDICATE
    #         ?{3} {4} ?value_2 .
    #         bind (lcase(str(?value_2)) as ?trg_value)
    #     }}
    # }} ;
    #
    # ### 2. FINDING CANDIDATE MATCH
    # INSERT
    # {{
    #     ### MATCH FOUND
    #     GRAPH <{0}load02>
    #     {{
    #         ?{1} <{8}relatesTo> ?{3} .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
    #     GRAPH <{0}load01>
    #     {{
    #         ?{1} {2} ?src_value .
    #         ?{3} {4} ?trg_value .
    #     }}
    #     ### INTERMEDIATE DATASET VIA URI
    #    graph <{9}>
    #    {{
    #         ?intermediate_uri
    #             ?intPred_1 ?value_3 ;
    #             ?intPred_2 ?value_4 .
    #         bind (lcase(?value_3) as ?src_value)
    #         bind (lcase(?value_4) as ?trg_value)
    #    }}
    # }} ;
    #
    # ### 3. CREATING THE CORRESPONDENCES
    # INSERT
    # {{
    #     GRAPH <{10}>
    #     {{
    #         ?{1} ?newSingletons  ?{3} .
    #     }}
    #     ### SINGLETONS' METADATA
    #     GRAPH <{14}{15}>
    #     {{
    #         ?newSingletons
    #             rdf:singletonPropertyOf     alivocab:{12}{13} ;
    #             alivocab:hasEvidence        ?evidence .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### MATCH FOUND
    #     GRAPH <{0}load02>
    #     {{
    #         ?{1} <{8}relatesTo> ?{3} .
    #          bind( iri(replace("{11}{12}{13}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
    #     }}
    #     {{
    #         SELECT ?{1} ?{3} ?evidence
    #         {{
    #             ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
    #             GRAPH <{0}load01>
    #             {{
    #                 ?{1} {2} ?src_value .
    #                 ?{3} {4} ?trg_value .
    #                 BIND(concat("[", ?src_value, "] aligns with [", ?trg_value, "]") AS ?evidence)
    #             }}
    #         }}
    #     }}
    # }} ;
    #
    # DROP GRAPH <{0}load01> ;
    # DROP GRAPH <{0}load02>
    # """.format(
    #     # 0          1         2           3         4
    #     Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
    #     # 5                6        7        8            9
    #     specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
    #     # 10  11           12                  13
    #     None, Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
    #     # 14           15                      16           17
    #     Ns.singletons, specs[St.linkset_name], Ns.alivocab, Ns.prov
    # )

    query04 = """
    DROP SILENT GRAPH <{0}load00> ;
    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02>
    """.format(Ns.tmpgraph)

    # print insert
    # return insert
    # print query01, query02, query03, query04
    queries = [query01, query02, query03, query04]
    return queries


def spa_linkset_intermediate_query(specs):

    source = specs[St.source]
    target = specs[St.target]

    # REPLACE RDF TYPE "a" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in source and source[St.rdf_predicate] is not None:
        src_rdf_pred = source[St.rdf_predicate] \
            if Ls.nt_format(source[St.rdf_predicate]) else "<{}>".format(source[St.rdf_predicate])
    else:
        src_rdf_pred = "a"

    if St.rdf_predicate in target and target[St.rdf_predicate] is not None:
        trg_rdf_pred = target[St.rdf_predicate] \
            if Ls.nt_format(target[St.rdf_predicate]) else "<{}>".format(target[St.rdf_predicate])
    else:
        trg_rdf_pred = "a"

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = specs[St.source][St.graph_name]
    src_uri = specs[St.source][St.graph]
    # src_aligns = specs[St.source][St.aligns]

    trg_name = specs[St.target][St.graph_name]
    trg_uri = specs[St.target][St.graph]
    # trg_aligns = specs[St.target][St.aligns]

    """
        NAMESPACE
    """
    prefix = "\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
        "##################################################################",
        "### Linking {{{}}} to {{{}}} based on exact name".format(source[St.graph_name], target[St.graph_name]),
        "##################################################################",
        "prefix dataset:    <{}>".format(Ns.dataset),
        "prefix linkset:    <{}>".format(Ns.linkset),
        "prefix singleton:  <{}>".format(Ns.singletons),
        "prefix alivocab:   <{}>".format(Ns.alivocab),
        "prefix tmpgraph:   <{}>".format(Ns.tmpgraph),
        "prefix tmpvocab:   <{}>".format(Ns.tmpvocab))

    early_drop_query = """
    DROP SILENT GRAPH <{0}load00> ;
    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02> ;
    DROP SILENT GRAPH <{1}{2}>
    """.format(Ns.tmpgraph, Ns.singletons, specs[St.linkset_name])

    # query = prefix + """
    #
    # ### 1.1. LOADING SOURCE TO A TEMPORARY GRAPH
    # INSERT
    # {{
    #     GRAPH <{0}load00>
    #     {{
    #         ### SOURCE DATASET AND ITS ALIGNED PREDICATE
    #         ?{1}_1 <{8}relatesTo1> ?SRC_trimmed .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE DATASET
    #     graph <{6}>
    #     {{
    #         ### SOURCE DATASET AND ITS ALIGNED PREDICATE
    #         ?{1}_1 {10} <{12}> .
    #         ?{1}_1 {2} ?value_1 .
    #
    #         # LOWER CASE OF THE VALUE
    #         BIND(lcase(str(?value_1)) as ?src_value)
    #
    #         # VALUE TRIMMING
    #         BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
    #         BIND(REPLACE(?src_value, ?regexp, '$1$2') AS ?SRC_trimmed)
    #     }}
    # }} ;
    #
    # ### 1.2. LOADING TARGET TO A TEMPORARY GRAPH
    # INSERT
    # {{
    #     GRAPH <{0}load01>
    #     {{
    #         ### TARGET DATASET AND ITS ALIGNED PREDICATE
    #         ?{3}_2 <{8}relatesTo3> ?TRG_trimmed .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### TARGET DATASET
    #     graph <{7}>
    #     {{
    #         ### TARGET DATASET AND ITS ALIGNED PREDICATE
    #         ?{3}_2 {11} <{13}> .
    #         ?{3}_2 {4} ?value_2 .
    #
    #         # LOWER CASE OF THE VALUE
    #         BIND(lcase(str(?value_2)) as ?trg_value)
    #
    #         # VALUE TRIMMING
    #         BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
    #         BIND(REPLACE(?trg_value, ?regexp, '$1$2') AS ?TRG_trimmed)
    #     }}
    # }} ;
    #
    # ### 2. FINDING CANDIDATE MATCH [PART 1]
    # INSERT
    # {{
    #     ### MATCH FOUND
    #     GRAPH <{0}load02>
    #     {{
    #         ?{1}_1 <{8}relatesTo> ?intermediate_uri .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
    #     GRAPH <{0}load00>
    #     {{
    #         ?{1}_1 <{8}relatesTo1> ?SRC_trimmed .
    #     }}
    #
    #     ### INTERMEDIATE DATASET VIA URI
    #     graph <{9}>
    #     {{
    #         ?intermediate_uri ?intPred_1 ?value ;
    #
    #         # LOWER CASE OF THE VALUE
    #         BIND(lcase(str(?value)) as ?INTERMEDIATE_val)
    #
    #         # VALUE TRIMMING
    #         BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
    #         BIND(REPLACE(?INTERMEDIATE_val, ?regexp, '$1$2') AS ?SRC_trimmed)
    #     }}
    # }} ;
    #
    # ### 3. FINDING CANDIDATE MATCH
    # INSERT
    # {{
    #     ### MATCH FOUND
    #     GRAPH <{0}load02>
    #     {{
    #         ?intermediate_uri <{8}relatesTo> ?{3}_2 .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
    #     GRAPH <{0}load02>
    #     {{
    #         ?{1}_1 <{8}relatesTo> ?intermediate_uri .
    #     }}
    #     GRAPH <{0}load01>
    #     {{
    #         ?{3}_2 <{8}relatesTo3> ?TRG_trimmed .
    #     }}
    #     ### INTERMEDIATE DATASET VIA URI
    #     graph <{9}>
    #     {{
    #         ?intermediate_uri ?intPred_1 ?value .
    #
    #         # LOWER CASE OF THE VALUE
    #         BIND(lcase(str(?value)) as ?INTERMEDIATE_val)
    #
    #         # VALUE TRIMMING
    #         BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
    #         BIND(REPLACE(?INTERMEDIATE_val, ?regexp, '$1$2') AS ?TRG_trimmed)
    #     }}
    # }}
    # """.format(
    #     # 0          1         2           3         4
    #     Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
    #     # 5                6        7        8            9
    #     specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
    #     # 10          11            12                          13
    #     src_rdf_pred, trg_rdf_pred, source[St.entity_datatype], target[St.entity_datatype]
    # )sou

    src_query = prefix + """

    ### 1.1. LOADING SOURCE TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH <{0}load00>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1}_1 <{4}relatesTo1> ?SRC_trimmed .
        }}
    }}
    WHERE
    {{
        ### SOURCE DATASET
        graph <{3}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1}_1 {5} <{6}> .
            ?{1}_1 {2} ?value_1 .

            # LOWER CASE OF THE VALUE
            BIND(lcase(str(?value_1)) as ?src_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?src_value, ?regexp, '$1$2') AS ?SRC_trimmed)
        }}
    }}

    """.format(
        # 0          1         2           3        4            5             6
        Ns.tmpgraph, src_name, src_aligns, src_uri, Ns.tmpvocab, src_rdf_pred, source[St.entity_datatype])


    trg_query = prefix + """
    ### 1.2. LOADING TARGET TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH <{0}load01>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{1}_2 <{2}relatesTo3> ?TRG_trimmed .
        }}
    }}
    WHERE
    {{
        ### TARGET DATASET
        graph <{3}>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{1}_2 {4} <{5}> .
            ?{1}_2 {6} ?value_2 .

            # LOWER CASE OF THE VALUE
            BIND(lcase(str(?value_2)) as ?trg_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?trg_value, ?regexp, '$1$2') AS ?TRG_trimmed)
        }}
    }}
    """.format(
        # 0          1         2            3         4            5                           6
        Ns.tmpgraph, trg_name, Ns.tmpvocab, trg_uri, trg_rdf_pred, target[St.entity_datatype], trg_aligns)


    match_query = prefix + """

    ### 2. FINDING CANDIDATE MATCH [PART 1]
    INSERT
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1}_1 <{3}relatesTo> ?intermediate_uri .
        }}
    }}
    WHERE
    {{
        ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
        GRAPH <{0}load00>
        {{
            ?{1}_1 <{3}relatesTo1> ?SRC_trimmed .
        }}

        ### INTERMEDIATE DATASET VIA URI
        graph <{4}>
        {{
            ?intermediate_uri ?intPred_1 ?value ;

            # LOWER CASE OF THE VALUE
            BIND(lcase(str(?value)) as ?INTERMEDIATE_val)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?INTERMEDIATE_val, ?regexp, '$1$2') AS ?SRC_trimmed)
        }}
    }} ;

    ### 3. FINDING CANDIDATE MATCH
    INSERT
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?intermediate_uri <{3}relatesTo> ?{2}_2 .
        }}
    }}
    WHERE
    {{
        ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
        GRAPH <{0}load02>
        {{
            ?{1}_1 <{3}relatesTo> ?intermediate_uri .
        }}
        GRAPH <{0}load01>
        {{
            ?{2}_2 <{3}relatesTo3> ?TRG_trimmed .
        }}
        ### INTERMEDIATE DATASET VIA URI
        graph <{4}>
        {{
            ?intermediate_uri ?intPred_1 ?value .

            # LOWER CASE OF THE VALUE
            BIND(lcase(str(?value)) as ?INTERMEDIATE_val)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?INTERMEDIATE_val, ?regexp, '$1$2') AS ?TRG_trimmed)
        }}
    }}
    """.format(
        # 0          1         3  2        8 3        9 4
        Ns.tmpgraph, src_name,  trg_name, Ns.tmpvocab, specs[St.intermediate_graph])


    linkset_query = prefix + """
    ### 3. CREATING THE CORRESPONDENCES
    INSERT
    {{
        GRAPH <{5}>
        {{
            ?{1}_1 ?newSingletons  ?{3}_2 .
        }}
        ### SINGLETONS' METADATA
        GRAPH <{10}{11}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{8}{9} ;
                alivocab:hasStrength        1 ;
                alivocab:hasEvidence        ?evidence .
        }}
    }}
    WHERE
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1}_1 <{6}relatesTo> ?intermediate_uri .
            ?intermediate_uri <{6}relatesTo> ?{3}_2 .
        }}

        bind( iri(replace("{7}{8}{9}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )

        {{
            SELECT ?{1}_1 ?{3}_2 ?evidence
            {{
                ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
                GRAPH <{0}load00>
                {{
                    ?{1}_1 <{6}relatesTo1> ?src_value .
                }}
                GRAPH <{0}load01>
                {{
                    ?{3}_2 <{6}relatesTo3> ?trg_value .
                }}
                BIND(concat("[", ?src_value, "] aligns with [", ?trg_value, "]") AS ?evidence)
            }}
        }}
    }}
    """.format(
        # 0          1         2           3         4           5                  6
        Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns, specs[St.linkset], Ns.tmpvocab,
        # 7          8                    9                      10             11
        Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount], Ns.singletons, specs[St.linkset_name])
    # insert = """
    # PREFIX alivocab:    <{16}>
    # PREFIX prov:        <{17}>
    #
    # DROP SILENT GRAPH <{0}load01> ;
    # DROP SILENT GRAPH <{0}load02> ;
    # DROP SILENT GRAPH <{10}> ;
    # DROP SILENT GRAPH <{14}{15}> ;
    #
    # ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    # INSERT
    # {{
    #     GRAPH <{0}load01>
    #     {{
    #         ### SOURCE DATASET AND ITS ALIGNED PREDICATE
    #         ?{1} {2} ?src_value .
    #         ### TARGET DATASET AND ITS ALIGNED PREDICATE
    #         ?{3} {4} ?trg_value .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE DATASET
    #     graph <{6}>
    #     {{
    #         ### SOURCE DATASET AND ITS ALIGNED PREDICATE
    #         ?{1} {2} ?value_1 .
    #         bind (lcase(str(?value_1)) as ?src_value)
    #     }}
    #     ### TARGET DATASET
    #     graph <{7}>
    #     {{
    #         ### TARGET DATASET AND ITS ALIGNED PREDICATE
    #         ?{3} {4} ?value_2 .
    #         bind (lcase(str(?value_2)) as ?trg_value)
    #     }}
    # }} ;
    #
    # ### 2. FINDING CANDIDATE MATCH
    # INSERT
    # {{
    #     ### MATCH FOUND
    #     GRAPH <{0}load02>
    #     {{
    #         ?{1} <{8}relatesTo> ?{3} .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
    #     GRAPH <{0}load01>
    #     {{
    #         ?{1} {2} ?src_value .
    #         ?{3} {4} ?trg_value .
    #     }}
    #     ### INTERMEDIATE DATASET VIA URI
    #    graph <{9}>
    #    {{
    #         ?intermediate_uri
    #             ?intPred_1 ?value_3 ;
    #             ?intPred_2 ?value_4 .
    #         bind (lcase(?value_3) as ?src_value)
    #         bind (lcase(?value_4) as ?trg_value)
    #    }}
    # }} ;
    #
    # ### 3. CREATING THE CORRESPONDENCES
    # INSERT
    # {{
    #     GRAPH <{10}>
    #     {{
    #         ?{1} ?newSingletons  ?{3} .
    #     }}
    #     ### SINGLETONS' METADATA
    #     GRAPH <{14}{15}>
    #     {{
    #         ?newSingletons
    #             rdf:singletonPropertyOf     alivocab:{12}{13} ;
    #             alivocab:hasEvidence        ?evidence .
    #     }}
    # }}
    # WHERE
    # {{
    #     ### MATCH FOUND
    #     GRAPH <{0}load02>
    #     {{
    #         ?{1} <{8}relatesTo> ?{3} .
    #          bind( iri(replace("{11}{12}{13}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
    #     }}
    #     {{
    #         SELECT ?{1} ?{3} ?evidence
    #         {{
    #             ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
    #             GRAPH <{0}load01>
    #             {{
    #                 ?{1} {2} ?src_value .
    #                 ?{3} {4} ?trg_value .
    #                 BIND(concat("[", ?src_value, "] aligns with [", ?trg_value, "]") AS ?evidence)
    #             }}
    #         }}
    #     }}
    # }} ;
    #
    # DROP GRAPH <{0}load01> ;
    # DROP GRAPH <{0}load02>
    # """.format(
    #     # 0          1         2           3         4
    #     Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
    #     # 5                6        7        8            9
    #     specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
    #     # 10  11           12                  13
    #     None, Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
    #     # 14           15                      16           17
    #     Ns.singletons, specs[St.linkset_name], Ns.alivocab, Ns.prov
    # )

    drop_query = """
    DROP SILENT GRAPH <{0}load00> ;
    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02>
    """.format(Ns.tmpgraph)

    # print insert
    # return insert
    # print query01, query02, query03, query04
    queries = [early_drop_query, src_query, trg_query, match_query, linkset_query, drop_query]
    return queries


def specs_2_linkset_intermediate(specs, display=False, activated=False):

    # if activated is True:
    heading = "======================================================" \
              "========================================================" \
              "\nEXECUTING LINKSET VIA INTERMEDIATE SPECS"

    print heading
    # inserted_mapping = None
    # inserted_linkset = None

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT BEFORE YOU DO ANYTHING
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    if specs[St.sameAsCount]:

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        # GENERATE THE NAME OF THE LINKSET
        Ls.set_linkset_name(specs)

        # SET THE INSERT QUERY
        specs[St.linkset_insert_queries] = spa_linkset_intermediate_query(specs)

        # GENERATE THE LINKSET
        # print "specs_2_linkset FUNCTION ACTIVATED: {}".format(activated)
        inserted_linkset = spa_linksets(specs, display=display, activated=activated)

        # REGISTER THE ALIGNMENT
        if inserted_linkset[St.message].__contains__("ALREADY EXISTS"):
            Urq.register_alignment_mapping(specs, created=False)
        else:
            Urq.register_alignment_mapping(specs, created=True)

        # SPA_LINKSET returns
        # {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}
        return inserted_linkset

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# NUMERICAL APPROXIMATION
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def insert_query_numeric_reduce(specs):

    # UPDATE THE SPECS OF SOURCE AND TARGETS
    # update_specification(specs[St.source])
    # update_specification(specs[St.target])
    # Ls.set_linkset_name(specs)
    # source = specs[St.source]
    # target = specs[St.target]

    prefix = """
    prefix dataset:    <{}>
    prefix linkset:    <{}>
    prefix singleton:  <{}>
    prefix alivocab:   <{}>
    prefix tmpgraph:   <{}>
    prefix tmpvocab:   <{}>
    """.format(Ns.dataset, Ns.linkset, Ns.singletons, Ns.alivocab, Ns.tmpgraph, Ns.tmpvocab)

    drop_q1 = """
    DROP SILENT GRAPH <{0}load_1> ;
    DROP SILENT GRAPH <{0}load_2> ;
    DROP SILENT GRAPH <{0}load_3> ;
    DROP SILENT GRAPH <{1}> ;
    DROP SILENT GRAPH <{2}{3}>
    """.format(Ns.tmpgraph, specs[St.linkset], Ns.singletons, specs[St.linkset_name])

    drop_q2 = """
    #DROP SILENT GRAPH <{0}load_1> ;
    #DROP SILENT GRAPH <{0}load_2> ;
    DROP SILENT GRAPH <{0}load_3>
    """.format(Ns.tmpgraph)

    source_extract = extract_query(specs, is_source=True)
    target_extract = extract_query(specs, is_source=False)
    match = match_numeric_query(specs)

    query_1 = drop_q1
    query_2 = prefix + source_extract + target_extract + match[0]
    query_3 = prefix + match[1]
    query_4 = drop_q2
    print query_1
    print query_2
    print query_3
    print query_4
    return [query_1, query_2, query_3, query_4]


########################################################################################
#                                                                                      #
########################################################################################


def pred_match(dataset_list):

    def helper1(index, predicate, obj):
        sparql_query = "?{} <{}> ?{} .".format(index, predicate, obj)
        return [" ?{}".format(obj), sparql_query, ]

    def helper2(graph_uri, triple_lines):
        sparql_query = """
    GRAPH <{}>
    {{
        {}
    }}""".format(graph_uri, triple_lines)
        return sparql_query

    pred_count = 0
    dataset_dict = dict()
    if type(dataset_list) is list:
        # For each dataset, gather its predicates
        for dataset in dataset_list:
            predicates = Qry.get_properties(dataset)
            # Load it into the dictionary
            if predicates is not None:
                # going through the predicates
                for i in range(1, len(predicates)):
                    if predicates[i][0] != "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        local_name = Ut.get_uri_local_name(predicates[i][0])

                        # Insert a new key
                        if local_name not in dataset_dict:
                            pred_count += 1
                            temp_dict = dict()
                            temp_dict[pred_count] = [dataset, predicates[i][0]]
                            dataset_dict[local_name] = temp_dict

                        # we found a match in property name
                        else:
                            pred_count += 1
                            curr_dict = dataset_dict[local_name]
                            curr_dict[pred_count] = [dataset, predicates[i][0]]

    # Write the SPARQL query for checking whether there is an actual match
    query = "SELECT DISTINCT"
    sub_query = ""
    group = dict()
    pre_dict = dict()
    for pred, data in dataset_dict.items():

        if len(data) > 1:
            for key, value in data.items():
                dataset = value[0]
                prd = value[1]
                dataset_name = Ut.get_uri_local_name(dataset)

                if dataset not in group:
                    line = helper1(dataset_name, prd, pred)
                    group[dataset] = line[1]
                    if line[0] not in pre_dict:
                        pre_dict[line[0]] = pred

                else:
                    line = helper1(dataset_name, prd, pred)
                    group[dataset] += "\n\t\t{}".format(line[1])
                    if line[0] not in pre_dict:
                        pre_dict[line[0]] = pred

                # print group[dataset]
    for key in pre_dict:
        query += " {}".format(key)
    for graph, triples in group.items():
        sub_query += helper2(graph, triples)
    #             result = helper(key, value[0], value[1])
    #             sub_query += result[1]
    #             query += result[0]

    query = "{}\n{{{}\n}}".format(query, sub_query)
    response = Qry.sparql_xml_to_matrix(query)
    print query
    if response is None:
        print "No match"


def insert_query_reduce2(specs):
    # UPDATE THE SPECS OF SOURCE AND TARGETS

    update_specification(specs[St.source])
    update_specification(specs[St.target])
    Ls.set_linkset_name(specs)

    source = specs[St.source]
    target = specs[St.target]

    # REPLACE RDF TYPE "a" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in source and source[St.rdf_predicate] is not None:
        src_rdf_pred = source[St.rdf_predicate] \
            if Ls.nt_format(source[St.rdf_predicate]) else "<{}>".format(source[St.rdf_predicate])
    else:
        src_rdf_pred = "a"

    if St.rdf_predicate in target and target[St.rdf_predicate] is not None:
        trg_rdf_pred = target[St.rdf_predicate] \
            if Ls.nt_format(target[St.rdf_predicate]) else "<{}>".format(target[St.rdf_predicate])
    else:
        trg_rdf_pred = "a"

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = source[St.graph_name]
    src_uri = source[St.graph]

    trg_name = specs[St.target][St.graph_name]
    trg_uri = specs[St.target][St.graph]

    prefix = """
    prefix dataset:    <{}>
    prefix linkset:    <{}>
    prefix singleton:  <{}>
    prefix alivocab:   <{}>
    prefix tmpgraph:   <{}>
    prefix tmpvocab:   <{}>
    """.format(Ns.dataset, Ns.linkset, Ns.singletons, Ns.alivocab, Ns.tmpgraph, Ns.tmpvocab)

    drop_q1 = """
    DROP SILENT GRAPH <{0}load00> ;
    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02> ;
    DROP SILENT GRAPH <{1}> ;
    DROP SILENT GRAPH <{2}{3}> ;
    """.format(Ns.tmpgraph, specs[St.linkset], Ns.singletons, specs[St.linkset_name])

    drop_q2 = """
    DROP SILENT GRAPH <{0}load00> ;
    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02>
    """.format(Ns.tmpgraph)

    if St.reducer not in source:
        src_reducer_comment = "#"
        src_reducer = ""
    else:
        src_reducer_comment = ""
        src_reducer = source[St.reducer]

    source_q = """
    INSERT
    {{
        GRAPH <{0}load00>
        {{
            ?{5}  {3}  ?label .
        }}
    }}
    WHERE
    {{
        GRAPH <{1}>
        {{
            ?{5}  {2}  ?<{7}> .
            ?{5}  {3}  ?object .
            BIND(lcase(str(?object)) as ?label)
        }}

        {6}FILTER NOT EXISTS
        {6}{{
        {6}    GRAPH <{4}>
        {6}    {{
        {6}        {{ ?{5}   ?pred   ?obj . }}
        {6}        UNION
        {6}        {{ ?obj   ?pred   ?{5}. }}
        {6}    }}
        {6}}}
    }} ;
    """.format(Ns.tmpgraph, src_uri, src_rdf_pred, src_aligns,
               src_reducer, src_name, src_reducer_comment, source[St.entity_datatype])

    if St.reducer not in target:
        trg_reducer_comment = "#"
        trg_reducer = ""
    else:
        trg_reducer_comment = ""
        trg_reducer = target[St.reducer]

    target_q = """
    INSERT
    {{
        GRAPH <{0}load01>
        {{
            ?{5}  {3}  ?label .
        }}
    }}
    WHERE
    {{
        GRAPH <{1}>
        {{
            ?{5}  {2}  ?<{7}> .
            ?{5}  {3}  ?object .
            BIND(lcase(str(?object)) as ?label)
        }}

        {6}FILTER NOT EXISTS
        {6}{{
        {6}  GRAPH <{4}>
        {6}  {{
        {6}    {{ ?{5}   ?pred   ?obj . }}
        {6}    UNION
        {6}    {{ ?obj   ?pred   ?{5} . }}
        {6}  }}
        {6}}}
    }} ;
    """.format(Ns.tmpgraph, trg_uri, trg_rdf_pred, trg_aligns,
               trg_reducer, trg_name, trg_reducer_comment, target[St.entity_datatype])

    query = prefix + drop_q1 + source_q + target_q + drop_q2
    print query
    return query


########################################################################################
# See if this makes sens or is necessary
########################################################################################

# def approx_numeric(specs):
#     query = """
#     select ?s ?x ?y
#     {
#         # SOURCE
#         graph dataset:leidenRanking_2015
#         {
#           ?s <http://risis.eu/leidenRanking_2015/ontology/predicate/Int_coverage> ?x .
#           ?s <http://risis.eu/leidenRanking_2015/ontology/predicate/MNCS> ?y .
#
#           filter( abs( xsd:decimal(?x) - xsd:decimal(?y) ) <= 0.1)
#
#         }
#     }
#     """
#
#     specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])
#
#     # UPDATE THE SPECS OF SOURCE AND TARGETS
#     update_specification(specs[St.source])
#     update_specification(specs[St.target])
#
#     # GENERATE THE NAME OF THE LINKSET
#     Ls.set_linkset_name(specs)
#
#     insert_query_numeric_reduce(specs)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    LINKSET FROM CLUSTERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def cluster_specs_2_linksets(specs, activated=False):

    # if activated is True:
    heading = "======================================================" \
              "========================================================" \
              "\nEXECUTING LINKSET SPECS"

    print heading

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT BEFORE YOU DO ANYTHING
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    if specs[St.sameAsCount]:

        # GENERATE THE NAME OF THE LINKSET
        Ls.set_cluster_linkset_name(specs)
        # print specs[St.linkset_name]

        check = Ls.run_checks_cluster(specs, check_type="linkset")
        # print check

        message = Ec.ERROR_CODE_4.replace('\n', "<br/>")
        if activated is True:

            # REGISTER THE ALIGNMENT
            if check[St.message].__contains__("ALREADY EXISTS"):
                Urq.register_alignment_mapping(specs, created=False)
            else:
                linkset_from_clusters(specs=specs, activated=True)
                message = "The linkset was created as [{}] with {} triples found!".format(
                    specs[St.linkset], specs[St.triples])
                Urq.register_alignment_mapping(specs, created=True)

            return {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

        return {St.message: message, St.error_code: 4, St.result: None}

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    GEO-SIMILARITY
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def geo_query(specs, is_source):

    # UPDATE THE SPECS OF SOURCE AND TARGETS
    if is_source is True:
        info = specs[St.source]
        load = "_1"
    else:
        info = specs[St.target]
        load = "_2"

    # REPLACE RDF TYPE "rdf:type" IN CASE ANOTHER TYPE IS PROVIDED
    if St.rdf_predicate in info and info[St.rdf_predicate] is not None:
        rdf_pred = info[St.rdf_predicate] \
            if Ls.nt_format(info[St.rdf_predicate]) else "<{}>".format(info[St.rdf_predicate])
    else:
        rdf_pred = "a"

    # FORMATTING THE LONGITUDE PROPERTY
    longitude = info[St.longitude] \
        if Ls.nt_format(info[St.longitude]) else "<{}>".format(info[St.longitude])

    # FORMATTING THE LATITUDE PROPERTY
    latitude = info[St.latitude] \
        if Ls.nt_format(info[St.latitude]) else "<{}>".format(info[St.latitude])

    # EXTRACTING THE RESOURCE GRAPH URI LOCAL NAME
    # name = info[St.graph_name]

    # EXTRACTING THE RESOURCE GRAPH URI
    uri = info[St.graph]

    # ADD THE REDUCER IF SET
    # if St.reducer not in info:
    #     reducer_comment = "#"
    #     reducer = ""
    # else:
    #     reducer_comment = ""
    #     reducer = info[St.reducer]

    if is_source is True:
        message = """######################################################################
    ### INSERTING DATA FROM THE SOURCE
    ######################################################################"""
    else:
        message = """######################################################################
    ### INSERTING MESSAGE FROM THE TARGET
    ######################################################################"""

    query = """
    {5}
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX wgs:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
    INSERT
    {{
        GRAPH <{0}load{1}>
        {{
            ?resource  wgs:long  ?longitude .
            ?resource  wgs:lat   ?latitude .
        }}
    }}
    WHERE
    {{
        GRAPH <{2}>
        {{
            ### LOCATION COORDINATES
            ?resource  {6}  <{7}> .
            ?resource  {3}  ?long .
            ?resource  {4}  ?lat .

            ### MAKING SURE THE COORDINATES ARE WELL FORMATTED
            BIND( STRDT(REPLACE(STR(?long), ",", "."), xsd:float)  as ?longitude )
            BIND( STRDT(REPLACE(STR(?lat), ",", "."), xsd:float)  as ?latitude )

            ### MAKING SURE THE COORDINATES AT DIGITS AND NOT LITERALS
            Filter (?longitude >= 0 || ?longitude <= 0 )
            Filter (?latitude  >= 0 || ?latitude  <= 0 )

            ### GENERATE A LOCATION URI
            BIND( replace("http://risis.eu/#","#", STRAFTER(str(UUID()),"uuid:")) as ?name )
            BIND(iri(?name) as ?location)
        }}
    }}
    """.format(
        # 0          1     2    3          4         5        6         7
        Ns.tmpgraph, load, uri, longitude, latitude, message, rdf_pred, info[St.entity_datatype])
    # print query
    return query


def geo_match_query(specs):

    # Note that for WKT formatted points,
    # the location is <long, lat>. The location of the White House can also be encoded using the WGS 84

    # source = specs[St.source]
    # target = specs[St.target]

    is_de_duplication = (specs[St.source][St.graph] == specs[St.target][St.graph]) and \
                        (specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype])

    # operator = "<" if specs[St.source][St.entity_datatype] == specs[St.target][St.entity_datatype] else "!="

    # comment = "" if is_de_duplication is True else "#"
    number_of_load = '1' if is_de_duplication is True else "2"
    unit = "{}(s)".format(Ut.get_uri_local_name(specs[St.unit]).lower())

    match = """
    ######################################################################
    ### INSETTING MATCH FOUND IN A TEMPORARY GRAPH
    ######################################################################
    PREFIX ll:          <{0}>
    PREFIX tmpvocab:    <{0}>
    PREFIX tmpgraph:    <{1}>
    prefix linkset:     <{5}>
    prefix singleton:   <{7}>
    PREFIX geof:        <http://www.opengis.net/def/function/geosparql/>
    PREFIX wgs:         <http://www.w3.org/2003/01/geo/wgs84_pos#>
    INSERT
    {{

        GRAPH linkset:{6}
        {{
            ?src_resource  ?singPre  ?trg_resource .
        }}

        GRAPH singleton:{6}
        {{
            ?singPre rdf:singletonPropertyOf     ll:nearbyGeoSim{10} .
            ?singPre ll:hasEvidence             "Near each other by at most {3} {9}" .
            ?singPre ll:hasStrength             1 .
        }}
    }}
    WHERE
    {{
        ### SOURCE DATASET WITH GEO-COORDINATES
        GRAPH tmpgraph:load_1
        {{
            ?src_resource  wgs:long  ?src_longitude .
            ?src_resource  wgs:lat   ?src_latitude .
            ### Create A SINGLETON URI
            BIND( replace("{0}{8}_#", "#", STRAFTER(str(UUID()),"uuid:")) as ?pre )
            BIND( iri(?pre) as ?singPre )
        }}
        ### TARGET DATASET WITH GEO-COORDINATES
        GRAPH tmpgraph:load_{2}
        {{
            ?trg_resource  wgs:long  ?trg_longitude .
            ?trg_resource  wgs:lat   ?trg_latitude .
        }}
        ### MATCHING TARGETS NEAR BY SOURCE
        ?src_resource  geof:nearby (?trg_resource {3} <{4}>).
    }}
    """.format(
        # 0          1            2               3                     4
        Ns.alivocab, Ns.tmpgraph, number_of_load, specs[St.unit_value], specs[St.unit],
        # 5         6                       7              8                    9     10
        Ns.linkset, specs[St.linkset_name], Ns.singletons, specs[St.mechanism], unit, specs[St.sameAsCount]
    )
    # print match
    return match


def geo_match(specs):

    # geo_query(ls_specs_1, True)
    # geo_query(ls_specs_1, False)
    # geo_match_query(ls_specs_1)
    drop = """
    PREFIX tmp: <{0}>
    DROP SILENT GRAPH tmp:load_1 ;
    drop silent graph tmp:load_2
    """.format(Ns.tmpgraph)

    print "\n\t>>> DROPPING GRAPH LOAD-1 &LOAD-2 IF THEY EXIST"
    print "\t", Qry.boolean_endpoint_response(drop)

    print "\n\t>>> LOADING SOURCE INTO GRAPH LOAD-1"
    print "\t", Qry.boolean_endpoint_response(geo_query(specs, True))

    print "\n\t>>> LOADING SOURCE INTO GRAPH LOAD-2"
    print "\t", Qry.boolean_endpoint_response(geo_query(specs, False))

    print "\n\t>>> LOOKING FOR GEO-SIM BETWEEN SOURCE AND TARGET"
    print "\t", Qry.boolean_endpoint_response(geo_match_query(specs))

    print "\n\t>>> DROPPING GRAPH LOAD-1 &LOAD-2"
    print "\t", Qry.boolean_endpoint_response(drop)


def geo_specs_2_linkset(specs, activated=False):

    # if activated is True:
    heading = "======================================================" \
              "========================================================" \
              "\nEXECUTING LINKSET SPECS FOR GEO-SIMILARITY"

    print heading

    if activated is False:
        print "THE FUNCTION IS NOT ACTIVATED" \
              "\n======================================================" \
              "========================================================"
        return {St.message: "THE FUNCTION IS NOT ACTIVATED.", St.error_code: 1, St.result: None}

    source = specs[St.source]
    target = specs[St.target]

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT BEFORE YOU DO ANYTHING
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])

    if specs[St.sameAsCount]:

        # UPDATE THE SPECS OF SOURCE AND TARGETS
        update_specification(specs[St.source])
        update_specification(specs[St.target])

        Ls.set_linkset_name(specs)
        # print specs[St.linkset_name]

        check = Ls.run_checks(specs, check_type="linkset")
        print check

        message = Ec.ERROR_CODE_4.replace('\n', "<br/>")
        if activated is True:

            # REGISTER THE ALIGNMENT
            if check[St.message].__contains__("ALREADY EXISTS"):
                Urq.register_alignment_mapping(specs, created=False)
            else:
                ########################################################################
                print """\n1. EXECUTING THE GEO-MATCH                                   """
                ########################################################################
                geo_match(specs)

                ########################################################################
                print """\n2. EXTRACT THE NUMBER OF TRIPLES                           """
                ########################################################################
                specs[St.triples] = Qry.get_namedgraph_size("{0}{1}".format(Ns.linkset, specs[St.linkset_name]))

                ########################################################################
                print """\n3. ASSIGN THE SPARQL INSERT QUERY                         """
                ########################################################################
                specs[St.insert_query] = "{} ;\n{};\n{}".format(
                    geo_query(specs, True), geo_query(specs, False), geo_match_query(specs))
                # print "INSERT QUERY: {}".format(specs[St.insert_query])

                if specs[St.triples] > 0:

                    ########################################################################
                    print """\n4. INSERTING THE GENERIC METADATA                         """
                    ########################################################################
                    metadata = Gn.linkset_geo_metadata(specs)
                    Qry.boolean_endpoint_response(metadata)

                    ########################################################################
                    print """\n5. WRITING TO FILE                                         """
                    ########################################################################
                    src = [source[St.graph_name], "", source[St.entity_ns]]
                    trg = [target[St.graph_name], "", target[St.entity_ns]]

                    # linkset_path = "D:\datasets\Linksets\ExactName"
                    linkset_path = DIRECTORY
                    writelinkset(src, trg, specs[St.linkset_name], linkset_path, metadata)
                    server_message = "Linksets created as: {}".format(specs[St.linkset])
                    message = "The linkset was created as [{}] with {} triples found!".format(
                        specs[St.linkset], specs[St.triples])

                    print "\n\t", server_message

                    Urq.register_alignment_mapping(specs, created=True)

                    print "\t*** JOB DONE! ***"

            return {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

        return {St.message: message, St.error_code: 4, St.result: None}

    else:
        print Ec.ERROR_CODE_1
        return {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}


grid = {
    St.rdf_predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    St.graph: "http://risis.eu/dataset/grid_20170712",
    St.entity_datatype: "http://xmlns.com/foaf/0.1/Organization",
    St.crossCheck: "http://www.w3.org/2000/01/rdf-schema#label",
    St.longitude: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#long>",
    St.latitude: "<http://www.grid.ac/ontology/hasAddress>/<http://www.w3.org/2003/01/geo/wgs84_pos#lat>"
}

eter_english = {
   St.graph: "http://risis.eu/dataset/eter_2014",
   St.entity_datatype: "http://risis.eu/eter_2014/ontology/class/University",
   St.crossCheck: "http://risis.eu/eter_2014/ontology/predicate/English_Institution_Name",
   St.longitude: "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__longitude",
   St.latitude: "http://risis.eu/eter_2014/ontology/predicate/Geographic_coordinates__latitude"
}

""" DEFINE LINKSET SPECIFICATIONS """
ls_specs_1 = {
    St.unit: Ns.meter,
    St.unit_value: 10,
    St.researchQ_URI: "http://risis.eu/activity/idea_3fd3a8",
    St.source: eter_english,
    St.target: grid,
    St.mechanism: "nearbyGeoSim",
}

leiden_1 = {
    St.rdf_predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
    St.graph: "http://risis.eu/dataset/leidenRanking_2015",
    St.entity_datatype: "http://risis.eu/leidenRanking_2015/ontology/class/University",
    St.aligns: "http://risis.eu/leidenRanking_2015/ontology/predicate/Int_coverage"}

leiden_2 = {
   St.rdf_predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
   St.graph: "http://risis.eu/dataset/leidenRanking_2015",
   St.entity_datatype: "http://risis.eu/leidenRanking_2015/ontology/class/University",
   St.aligns: "http://risis.eu/leidenRanking_2015/ontology/predicate/MNCS"}

ls_specs_2 = {
    St.researchQ_URI: "",
    St.source: leiden_1,
    St.target: leiden_2,
    St.mechanism: "approxNbrSim",
    St.delta: 1,
    St.numeric_approx_type: "number"
}

# insert_query_reduce(ls_specs_1)

# approx_numeric(ls_specs_2)

# specs_2_linkset_num_approx(ls_specs_2, match_numeric=True, activated=True)

# geo_match(ls_specs_1)

# geo_specs_2_linkset(ls_specs_1, activated=True)
# update with link strength of 1 for near by geo-sim

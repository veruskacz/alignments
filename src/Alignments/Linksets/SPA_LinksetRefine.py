
import Alignments.Query as Qry
import Alignments.Settings as St
import Alignments.NameSpace as Ns
import Alignments.ErrorCodes as Ec
import Alignments.GenericMetadata as Gn
import Alignments.Linksets.Linkset as Ls
import Alignments.Utility as Ut
import Alignments.Lenses.Lens_Difference as Df
from Alignments.Utility import write_to_file, update_specification
from Alignments.UserActivities.UserRQ import register_alignment_mapping
import Alignments.Server_Settings as Ss
import cStringIO as Buffer


DIRECTORY = Ss.settings[St.linkset_Refined_dir]


def refine(specs, activated=False):

    if activated is True:
        print Ut.headings("EXECUTING LINKSET REFINE SPECS...")
    else:
        print Ut.headings("THE FUNCTION [refine] IS NOT ACTIVATED")
        return {St.message: Ec.ERROR_CODE_0, St.error_code: 0, St.result: None}

    try:

        insert_query = None

        if specs[St.mechanism] == 'exactStrSim':
            print "REFINING WITH EXACT STRING SIMILARITY"
            insert_query = refine_exact_query

        elif specs[St.mechanism] == 'intermediate':
            print "REFINING WITH INTERMEDIATE DATASET"
            insert_query = refine_intermediate_query

        elif specs[St.mechanism] == 'approxNbrSim':
            print "REFINING WITH NUMERICAL APPROXIMATION "
            insert_query = refine_numeric_query

        refined = {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
        diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 1, St.result: None}
        # result = {'refined': refined, 'difference': diff}

        if insert_query is not None:
            result = refining(specs, insert_query, activated=activated)

            return result

        else:
            return {'refined': refined, 'difference': diff}

    except Exception as err:
        print err.message
        refined = {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
        diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 1, St.result: None}
        return {'refined': refined, 'difference': diff}


def refining(specs, insert_query, save=False, activated=False):

    refined = {St.message: Ec.ERROR_CODE_1, St.error_code: 5, St.result: None}
    diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 1, St.result: None}

    # UPDATE THE SPECS VARIABLE
    # print "UPDATE THE SPECS VARIABLE"
    update_specification(specs)
    update_specification(specs[St.source])
    update_specification(specs[St.target])

    # ACCESS THE TASK SPECIFIC PREDICATE COUNT
    specs[St.sameAsCount] = Qry.get_same_as_count(specs[St.mechanism])
    # print "sameAsCount:", specs[St.sameAsCount]

    if specs[St.sameAsCount] is None:
        return {'refined': refined, 'difference': diff}

    # GENERATE THE NAME OF THE LINKSET
    Ls.set_refined_name(specs)
    # print "\nREFINED NAME:", specs[St.refined]
    # print "LINKSET TO REFINE BEFORE CHECK:", specs[St.linkset]

    # CHECK WHETHER OR NOT THE LINKSET WAS ALREADY CREATED
    check = Ls.run_checks(specs, check_type="refine")
    # print "\nREFINED NAME:", specs[St.refined]
    # print "LINKSET TO REFINE:", specs[St.linkset]

    if check[St.message] == "NOT GOOD TO GO":
        # refined = check[St.refined]
        # difference = check["difference"]
        return check

    # print "\nREFINED:", specs[St.refined]
    # print "LINKSET TO REFINE:", specs[St.linkset]
    # print "CHECK:", check

    # THE LINKSET DOES NOT EXIT, LETS CREATE IT NOW
    print Ls.refined_info(specs, specs[St.sameAsCount])

    # POINT TO THE LINKSET THE CURRENT LINKSET WAS DERIVED FROM
    print "1. wasDerivedFrom {}".format(specs[St.linkset])
    specs[St.derivedfrom] = "\t\tprov:wasDerivedFrom\t\t\t<{}> ;".format(specs[St.linkset])

    # print "REFINED NAME:",  specs[St.refined_name]
    # print "REFINED:", specs[St.refined]
    # print "LINKSET TO BE REFINED:", specs[St.linkset]

    print "\n2. RETRIEVING THE METADATA ABOUT THE GRAPH TO REFINE"
    # metadata_q = Qry.q_linkset_metadata(specs[St.linkset])
    metadata_q = """
    prefix ll:    <{}>
    SELECT DISTINCT ?type ?singletonGraph
    {{
        # LINKSET METADATA
        <{}>
            a                       ?type ;
            ll:singletonGraph		?singletonGraph .
    }}
    """.format(Ns.alivocab, specs[St.linkset])
    print "QUERY:", metadata_q
    matrix = Qry.sparql_xml_to_matrix(metadata_q)
    # print "\nMETA DATA: ", matrix

    if matrix:

        if matrix[St.message] == "NO RESPONSE":
            print Ec.ERROR_CODE_1
            print matrix[St.message]
            return {'refined': refined, 'difference': diff}

        elif matrix[St.result] is None:
            print matrix[St.message]
            returned = {St.message: matrix[St.message], St.error_code: 666, St.result: None}
            return {'refined': returned, 'difference': diff}

    else:
        print Ec.ERROR_CODE_1
        return {'refined': refined, 'difference': diff}

    # GET THE SINGLETON GRAPH OF THE LINKSET TO BE REFINED
    print "\n3. GETTING THE SINGLETON GRAPH OF THE GRAPH TO REFINE"
    specs[St.singletonGraph] = matrix[St.result][1][1]
    # print matrix[St.result][1][0]

    specs[St.insert_query] = insert_query(specs)
    # print specs[St.insert_query]

    # IF THE INSERT QUERY IS NOT A LIST
    if type(specs[St.insert_query]) == str:
        is_run = Qry.boolean_endpoint_response(specs[St.insert_query])

    # THE INSERT QUERY IS A LIST
    else:
        print "\n4. RUNNING THE DROP QUERY"
        print specs[St.insert_query][0]
        Qry.boolean_endpoint_response(specs[St.insert_query][0])

        print "\n5. RUNNING THE SOURCE TEMP QUERY"
        print specs[St.insert_query][1]
        Qry.boolean_endpoint_response(specs[St.insert_query][1])

        print "\n6. RUNNING THE TARGET TEMP QUERY"
        print specs[St.insert_query][2]
        Qry.boolean_endpoint_response(specs[St.insert_query][2])

        print "\n7. RUNNING THE FINDING QUERY"
        print specs[St.insert_query][3]
        is_run = Qry.boolean_endpoint_response(specs[St.insert_query][3])

        print "\n7. RUNNING THE FINAL DROP"
        print specs[St.insert_query][4]
        is_run = Qry.boolean_endpoint_response(specs[St.insert_query][4])

        print specs[St.insert_query][5]
        is_run = Qry.boolean_endpoint_response(specs[St.insert_query][5])

    print "\n>>> RUN SUCCESSFULLY:", is_run.upper()

    # NO INSERTION HAPPENED
    if is_run == "true" or is_run == Ec.ERROR_STARDOG_1:

        # GENERATE THE
        #   (1) LINKSET METADATA
        #   (2) LINKSET OF CORRESPONDENCES
        #   (3) SINGLETON METADATA
        # AND WRITE THEM ALL TO FILE

        print "GENERATING THE METADATA"
        pro_message = refine_metadata(specs, save=save)

        # SET THE RESULT ASSUMING IT WENT WRONG
        refined = {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}
        diff = {St.message: Ec.ERROR_CODE_4, St.error_code: 4, St.result: None}

        server_message = "Linksets created as: [{}]".format(specs[St.refined])
        message = "The linkset was created as [{}]. <br/>{}".format(specs[St.refined], pro_message)

        # MESSAGE ABOUT THE INSERTION STATISTICS
        print "\t", server_message

        if int(specs[St.triples]) > 0:

            # UPDATE THE REFINED VARIABLE AS THE INSERTION WAS SUCCESSFUL
            refined = {St.message: message, St.error_code: 0, St.result: specs[St.linkset]}

            print "REGISTERING THE ALIGNMENT"
            if refined[St.message].__contains__("ALREADY EXISTS"):
                register_alignment_mapping(specs, created=False)
            else:
                register_alignment_mapping(specs, created=True)

            try:
                print "\nCOMPUTE THE DIFFERENCE AND DOCUMENT IT"
                diff_lens_specs = {
                    St.researchQ_URI: specs[St.researchQ_URI],
                    St.subjectsTarget: specs[St.linkset],
                    St.objectsTarget: specs[St.refined]
                }
                diff = Df.difference(diff_lens_specs, save=save, activated=activated)
                message_2 = "\t>>> {} CORRESPONDENCES INSERTED AS THE DIFFERENCE".format(diff_lens_specs[St.triples])
                print message_2
            except Exception as err:
                print "THE DIFFERENCE FAILED: ", str(err.message)

            print "\tLinkset created as: ", specs[St.refined]
            print "\t*** JOB DONE! ***"

            return {'refined': refined, 'difference': diff}

        else:
            print ">>> NO TRIPLE WAS INSERTED BECAUSE NO MATCH COULD BE FOUND"
            return {'refined': refined, 'difference': diff}

    else:
        print "NO MATCH COULD BE FOUND."



########################################################################################
# LINKSET REFINEMENT QUERIES
########################################################################################

def refine_exact_query(specs):

    source = specs[St.source]
    target = specs[St.target]
    src_graph = source[St.graph] if St.extended_graph not in source else source[St.extended_graph]
    trg_graph = target[St.graph] if St.extended_graph not in target else target[St.extended_graph]
    print "src_graph:", src_graph
    print "trg_graph:", trg_graph

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    # GENERATE THE INSERT QUERY
    insert_query = """
    PREFIX prov:        <{}>
    PREFIX rdf:         <{}>
    PREFIX alivocab:    <{}>
    INSERT
    {{
        ### REFINED LINKSET
        GRAPH <{}>
        {{
            ?subject ?newSingletons ?object .
        }}

        ### SINGLETONS' METADATA
        GRAPH <{}{}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{}{} ;

                ## THIS IS THE TRAIL
                prov:wasDerivedFrom         ?singleton ;

                ## BUT THIS IS ADDED FOR QUERY SIMPLICITY AND EFFICIENCY
                ?sP ?sO ;

                ## THIS IS ITS OWN EVIDENCE
                alivocab:hasEvidence        ?trimmed .
        }}
    }}
    WHERE
    {{
        ### LINKSET
        GRAPH <{}>
        {{
            ?subject ?singleton ?object .
             bind( iri(replace("{}{}{}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}

        ### METADATA
        graph <{}>
        {{
            ?singleton ?sP ?sO .
        }}

        ### SOURCE DATASET
        GRAPH <{}>
        {{
            ?subject
                a   <{}> ;
                {} 	?s_label .
            BIND(lcase(str(?s_label)) as ?label1)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?label1, ?regexp, '$1$2') AS ?trimmed)
        }}

        ### TARGET DATASET
        GRAPH <{}>
        {{
            ?object
                a   <{}> ;
                {} 	?o_label .
            BIND(lcase(str(?o_label)) as ?label2)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?label2, ?regexp, '$1$2') AS ?trimmed)
        }}
    }}
    """.format(Ns.prov, Ns.rdf, Ns.alivocab,
               specs[St.refined], Ns.singletons, specs[St.refined_name], specs[St.mechanism], specs[St.sameAsCount],
               specs[St.linkset], Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
               specs[St.singletonGraph],
               src_graph, source[St.entity_datatype], src_aligns,
               trg_graph, target[St.entity_datatype], trg_aligns)
    # print insert_query
    return insert_query


def refine_intermediate_query(specs):

    source = specs[St.source]
    target = specs[St.target]

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = specs[St.source][St.graph_name]
    # src_uri = specs[St.source][St.graph]
    src_uri = source[St.graph] if St.extended_graph not in source else source[St.extended_graph]
    # src_aligns = specs[St.source][St.aligns]

    trg_name = specs[St.target][St.graph_name]
    # trg_uri = specs[St.target][St.graph]
    trg_uri = target[St.graph] if St.extended_graph not in target else target[St.extended_graph]
    # trg_aligns = specs[St.target][St.aligns]

    insert = """
    PREFIX alivocab:    <{16}>
    PREFIX prov:        <{17}>

    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02> ;
    DROP SILENT GRAPH <{10}> ;
    DROP SILENT GRAPH <{14}{15}> ;

    INSERT
    {{
        GRAPH <{10}>
        {{
            ?{1} ?newSingletons  ?{3} .
        }}
        ### SINGLETONS' METADATA
        GRAPH <{14}{15}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{12}{13} ;
                prov:wasDerivedFrom         ?pred ;
                alivocab:hasEvidence        ?evidence .
        }}
    }}

    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{1} ?pred  ?{3} .
            bind( iri(replace("{11}{12}{13}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}

        ### SOURCE DATASET
        graph <{6}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1} {2} ?value_1 .
            bind (lcase(str(?value_1)) as ?src_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?src_value, ?regexp, '$1$2') AS ?src_trimmed)
        }}

        ### TARGET DATASET
        graph <{7}>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3} {4} ?value_2 .
            bind (lcase(str(?value_2)) as ?trg_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?trg_value, ?regexp, '$1$2') AS ?trg_trimmed)
        }}

        ### INTERMEDIATE DATASET
        graph <{9}>
        {{
            ?intermediate_uri
                ?intPred_1 ?value_3 ;
                ?intPred_2 ?value_4 .

            ### VALUES TO LOWER CASE
            bind (lcase(str(?value_3)) as ?src_val)
            bind (lcase(str(?value_4)) as ?trg_val)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp )
            BIND(REPLACE(?src_val, ?regexp, '$1$2') AS ?src_trimmed)
            BIND(REPLACE(?trg_val, ?regexp, '$1$2') AS ?trg_trimmed)
            BIND(concat("[", ?src_trimmed, "] aligns with [", ?trg_trimmed, "]") AS ?evidence)
        }}
    }} ;

    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02>
    """.format(
        # 0          1         2           3         4
        Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
        # 5                6        7        8            9
        specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
        # 10               11           12                  13
        specs[St.refined], Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
        # 14           15                      16           17
        Ns.singletons, specs[St.refined_name], Ns.alivocab, Ns.prov
    )

    # print insert
    return insert


def refine_numeric_query(specs):

    # is_de_duplication = specs[St.source][St.graph] == specs[St.target][St.graph]
    # number_of_load = '1' if is_de_duplication is True else "2"

    # PLAIN NUMBER CHECK
    delta_check = "BIND(ABS(xsd:decimal(?x) - xsd:decimal(?x)) AS ?DELTA)"

    # DATE CHECK
    if specs[St.numeric_approx_type].lower() == "date":
        delta_check = "BIND( (YEAR(xsd:datetime(STR(?x))) - YEAR(xsd:datetime(STR(?y))) ) as ?DELTA )"

    source = specs[St.source]
    target = specs[St.target]

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = specs[St.source][St.graph_name]
    # src_uri = specs[St.source][St.graph]
    src_uri = source[St.graph] if St.extended_graph not in source else source[St.extended_graph]
    # src_aligns = specs[St.source][St.aligns]

    trg_name = specs[St.target][St.graph_name]
    # trg_uri = specs[St.target][St.graph]
    trg_uri = target[St.graph] if St.extended_graph not in target else target[St.extended_graph]
    # trg_aligns = specs[St.target][St.aligns]

    drop = """
    PREFIX ll:    <{0}>
    PREFIX prov:  <{1}>
    PREFIX tempG: <{2}>

    DROP SILENT GRAPH tempG:load_{5}_01 ;
    DROP SILENT GRAPH tempG:load_{5}_02 ;
    DROP SILENT GRAPH <{3}> ;
    DROP SILENT GRAPH <{4}{5}>
    """.format(
        # 0          1         2           3                  4              5
        Ns.alivocab, Ns.prov, Ns.tmpgraph, specs[St.refined], Ns.singletons, specs[St.refined_name]
    )

    drop_final_1 = """
    PREFIX tempG: <{0}>
    DROP SILENT GRAPH tempG:load_{1}_01
        """.format(
        # 0           1
        Ns.tmpgraph,  specs[St.refined_name]
    )

    drop_final_2 = """
    PREFIX tempG: <{0}>
    DROP SILENT GRAPH tempG:load_{1}_02
            """.format(
        # 0           1
        Ns.tmpgraph, specs[St.refined_name]
    )

    source = """
    PREFIX ll:    <{0}>
    PREFIX prov:  <{1}>
    PREFIX tempG: <{2}>

    ### 1. LOADING SOURCE TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH tempG:load_{7}_01
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{3}_1 ll:relatesTo1 ?srcTrimmed .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{4}>
        {{
            ?{3}_1 ?pred  ?obj .
        }}

        ### SOURCE DATASET
        graph <{5}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{3}_1 {6} ?value_1 .
            bind (lcase(str(?value_1)) as ?src_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?src_value, ?regexp, '$1$2') AS ?srcTrimmed)
        }}
    }}
    """.format(
        # 0          1         2           3         4                  5        6           7
        Ns.alivocab, Ns.prov, Ns.tmpgraph, src_name, specs[St.linkset], src_uri, src_aligns, specs[St.refined_name])

    target = """
    PREFIX ll:    <{0}>
    PREFIX prov:  <{1}>
    PREFIX tempG: <{2}>

    ### 1. LOADING SOURCE TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH tempG:load_{7}_01
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{3}_1 ll:relatesTo3 ?trgTrimmed .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{4}>
        {{
            ?sub ?pred ?{3}_1 .
        }}

        ### SOURCE DATASET
        graph <{5}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{3}_1 {6} ?value_1 .
            bind (lcase(str(?value_1)) as ?trg_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?trg_value, ?regexp, '$1$2') AS ?trgTrimmed)
        }}
    }}
    """.format(
        # 0          1         2           3         4                  5        6           7
        Ns.alivocab, Ns.prov, Ns.tmpgraph, trg_name, specs[St.linkset], trg_uri, trg_aligns, specs[St.refined_name])


    find = """
    ### 2. FINDING CANDIDATE MATCH BETWEEN THE SOURCE AND TARGET
    PREFIX ll:    <{0}>
    PREFIX prov:  <{1}>
    PREFIX tempG: <{2}>
    INSERT
    {{
        ### MATCH FOUND
        GRAPH <{10}>
        {{
            ?{3}_1 ?newSingletons ?{4}_2 .
        }}
        # METADATA OF MATCH FOUND
        GRAPH <{11}{12}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     ll:{8}{9} ;
                prov:wasDerivedFrom         ?pred ;
                ll:hasEvidence              ?evidence .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{3}_1 ?pred  ?{4}_2 .
            bind( iri(replace("{0}{8}{9}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}
        ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
        GRAPH tempG:load_{12}_01
        {{
            ?{3}_1 ll:relatesTo1 ?x .
            ?{4}_2 ll:relatesTo3 ?y .
        }}

        # DELTA APPROX CHECK
        {6}

        FILTER( ABS(?DELTA) <= {7} )

        BIND(concat("The DELTA of [", ?x, "] and [", ?y, "] is [", STR(ABS(?DELTA)),
        "] which passed the threshold of [", STR({7}), "]" ) AS ?evidence)
    }}""".format(
        # 0          1        2            3         4         5                  6            7
        Ns.alivocab, Ns.prov, Ns.tmpgraph, src_name, trg_name, specs[St.linkset], delta_check, specs[St.delta],
        # 8                  9                      10                 11             12
        specs[St.mechanism], specs[St.sameAsCount], specs[St.refined], Ns.singletons, specs[St.refined_name])

    return [drop, source, target, find, drop_final_1, drop_final_2]


def refine_nearby_geo_query(specs):
    ""

########################################################################################
# SINGLE PREDICATE ALIGNMENT FOR LINKSET REFINEMENT BASED ON INTERMEDIATE
########################################################################################
# DEPRECATED (TODO TO DELETE)
def refine_intermediate_query_1(specs):

    source = specs[St.source]
    target = specs[St.target]

    # FORMATTING THE ALIGNS PROPERTY
    src_aligns = source[St.aligns] \
        if Ls.nt_format(source[St.aligns]) else "<{}>".format(source[St.aligns])

    trg_aligns = target[St.aligns] \
        if Ls.nt_format(target[St.aligns]) else "<{}>".format(target[St.aligns])

    src_name = source[St.graph_name]
    # src_uri =source[St.graph]
    src_uri = source[St.graph] if St.extended_graph not in source else source[St.extended_graph]
    # src_aligns = specs[St.source][St.aligns]

    trg_name = specs[St.target][St.graph_name]
    # trg_uri = specs[St.target][St.graph]
    trg_uri = target[St.graph] if St.extended_graph not in target else target[St.extended_graph]
    # trg_aligns = specs[St.target][St.aligns]

    insert = """
    PREFIX alivocab:    <{16}>
    PREFIX prov:        <{17}>

    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02> ;
    DROP SILENT GRAPH <{10}> ;
    DROP SILENT GRAPH <{14}{15}> ;

    ### 1. LOADING SOURCE AND TARGET TO A TEMPORARY GRAPH
    INSERT
    {{
        GRAPH <{0}load01>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1} <{8}relatesTo1> ?src_trimmed .

            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3} <{8}relatesTo3> ?trg_trimmed .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{1} ?pred  ?{3} .
        }}
        ### SOURCE DATASET
        graph <{6}>
        {{
            ### SOURCE DATASET AND ITS ALIGNED PREDICATE
            ?{1} {2} ?value_1 .
            bind (lcase(str(?value_1)) as ?src_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?src_value, ?regexp, '$1$2') AS ?src_trimmed)
        }}
        ### TARGET DATASET
        graph <{7}>
        {{
            ### TARGET DATASET AND ITS ALIGNED PREDICATE
            ?{3} {4} ?value_2 .
            bind (lcase(str(?value_2)) as ?trg_value)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?trg_value, ?regexp, '$1$2') AS ?trg_trimmed)
        }}
    }} ;

    ### 2. FINDING CANDIDATE MATCH
    INSERT
    {{
        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1} <{8}relatesTo> ?{3} .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
            ?{1} ?pred  ?{3} .
        }}
        ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
        GRAPH <{0}load01>
        {{
            ?{1} <{8}relatesTo1> ?src_trimmed .
            ?{3} <{8}relatesTo3> ?trg_trimmed .
        }}
        ### INTERMEDIATE DATASET
       graph <{9}>
       {{
            ?intermediate_uri
                ?intPred_1 ?value_3 ;
                ?intPred_2 ?value_4 .
            bind (lcase(str(?value_3)) as ?src_val)
            bind (lcase(str(?value_4)) as ?trg_val)

            # VALUE TRIMMING
            BIND('^\\\\s+(.*?)\\\\s*$|^(.*?)\\\\s+$' AS ?regexp)
            BIND(REPLACE(?src_val, ?regexp, '$1$2') AS ?src_trimmed)
            BIND(REPLACE(?trg_val, ?regexp, '$1$2') AS ?trg_trimmed)
       }}
    }} ;

    ### 3. CREATING THE CORRESPONDENCES
    INSERT
    {{
        GRAPH <{10}>
        {{
            ?{1} ?newSingletons  ?{3} .
        }}
        ### SINGLETONS' METADATA
        GRAPH <{14}{15}>
        {{
            ?newSingletons
                rdf:singletonPropertyOf     alivocab:{12}{13} ;
                prov:wasDerivedFrom         ?pred ;
                alivocab:hasEvidence        ?evidence .
        }}
    }}
    WHERE
    {{
        ### LINKSET TO REFINE
        graph <{5}>
        {{
         ?{1} ?pred  ?{3} .
        }}

        ### MATCH FOUND
        GRAPH <{0}load02>
        {{
            ?{1} <{8}relatesTo> ?{3} .
             bind( iri(replace("{11}{12}{13}_#", "#",  strafter(str(uuid()), "uuid:") )) as ?newSingletons )
        }}
        {{
            SELECT ?{1} ?{3} ?evidence
            {{
                ### SOURCE AND TARGET LOADED TO A TEMPORARY GRAPH
                GRAPH <{0}load01>
                {{
                    ?{1} <{8}relatesTo1> ?src_value .
                    ?{3} <{8}relatesTo3> ?trg_value .
                    BIND(concat("[", ?src_value, "] aligns with [", ?trg_value, "]") AS ?evidence)
                }}
            }}
        }}
    }} ;

    DROP SILENT GRAPH <{0}load01> ;
    DROP SILENT GRAPH <{0}load02>
    """.format(
        # 0          1         2           3         4
        Ns.tmpgraph, src_name, src_aligns, trg_name, trg_aligns,
        # 5                6        7        8            9
        specs[St.linkset], src_uri, trg_uri, Ns.tmpvocab, specs[St.intermediate_graph],
        # 10               11           12                  13
        specs[St.refined], Ns.alivocab, specs[St.mechanism], specs[St.sameAsCount],
        # 14           15                      16           17
        Ns.singletons, specs[St.refined_name], Ns.alivocab, Ns.prov
    )

    # print insert
    return insert


########################################################################################
# SINGLE PREDICATE ALIGNMENT IDENTITY
# ALIGNING SUBJECTS FROM DIFFERENT GRAPHS THAT HAVE THE SAME RESOURCE URI IDENTIFIER
########################################################################################


def refine_metadata(specs, save=False):

    # GENERATE GENERIC METADATA
    metadata = Gn.linkset_refined_metadata(specs)

    if int(specs[St.triples]) > 0:

        # print metadata
        is_inserted = Qry.boolean_endpoint_response(metadata["query"])
        print ">>> THE METADATA IS SUCCESSFULLY INSERTED:", is_inserted


        if save is True:
            # GENERATE LINKSET CONSTRUCT QUERY
            construct_query = "\n{}\n{}\n{}\n{}\n{}\n".format(
                "PREFIX predicate: <{}>".format(Ns.alivocab),
                "PREFIX src{}: <{}>".format(specs[St.source][St.graph_name], specs[St.source][St.graph_ns]),
                "PREFIX trg{}: <{}>".format(specs[St.target][St.graph_name], specs[St.target][St.graph_ns]),
                "construct { ?x ?y ?z }",
                "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.refined]),
            )

            # GENERATE LINKSET SINGLETON METADATA QUERY
            singleton_metadata_query = "\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format(
                "PREFIX singMetadata:   <{}>".format(Ns.singletons),
                "PREFIX predicate:      <{}>".format(Ns.alivocab),
                "PREFIX prov:           <{}>".format(Ns.prov),
                "PREFIX rdf:            <{}>".format(Ns.rdf),
                "construct { ?x ?y ?z }",
                "where     {{ graph <{}> {{ ?x ?y ?z }} }}".format(specs[St.singleton]),
            )

            # GET THE CORRESPONDENCES INSERTED USING A THE CONSTRUCT QUERY
            singleton_construct = Qry.endpointconstruct(singleton_metadata_query)
            if singleton_construct is not None:
                singleton_construct = \
                    singleton_construct.replace('{', "singMetadata:{}\n{{".format(specs[St.refined_name]), 1)

            # GET THE SINGLETON METADATA USING THE CONSTRUCT QUERY
            construct_response = Qry.endpointconstruct(construct_query)
            if construct_response is not None:
                construct_response = construct_response.replace('{', "<{}>\n{{".format(specs[St.refined]), 1)

            # WRITE TO FILE
            print "\t>>> WRITING THE METADATA TO FILE TO FILE"
            write_to_file(graph_name=specs[St.refined_name], metadata=metadata["query"].replace("INSERT DATA", ""),
                          correspondences=construct_response, singletons=singleton_construct, directory=DIRECTORY)

    return metadata["message"]


def is_refinable(graph):

    print Ut.headings("IS {} REFINABLE?".format(graph))

    # x = "http://risis.eu/lens/union_Grid_20170712_H2020_P1626350579"
    description = Buffer.StringIO()

    query = """
    PREFIX bdb:         <{}>
    PREFIX void:        <{}>
    PREFIX ll:          <{}>
    SELECT DISTINCT ?subjectsTarget  ?objectsTarget ?subjectsDatatype ?objectsDatatype
    {{
        <{}>
            void:target|void:subjectsTarget|void:objectsTarget ?linkset .

        ?linkset
            void:objectsTarget		?objectsTarget ;
            void:subjectsTarget		?subjectsTarget ;
            bdb:objectsDatatype		?objectsDatatype ;
            bdb:subjectsDatatype	?subjectsDatatype .
    }}""".format(Ns.bdb, Ns.void, Ns.alivocab, graph)

    response = Qry.sparql_xml_to_matrix(query)
    # print response

    if response:
        result = response[St.result]
        if result is not None and len(result) == 2:
            description.write("\n>>> {} IS REFINABLE... \n>>> AS ALL LINKSETS INVOLVED IN "
                              "THE LENS SHARE THE SAME SPECIFICATION DESCRIBED BELOW ...".format(graph))
            for i in range(1, len(result)):
                description.write("\n\n\t{:17}: {}".format(result[0][0], result[i][0]))
                description.write("\n\t{:17}: {}".format(result[0][1], result[i][1]))
                description.write("\n\t{:17}: {}".format(result[0][2], result[i][2]))
                description.write("\n\t{:17}: {}\n".format(result[0][3], result[i][3]))

            print description.getvalue()
            return {St.message: True, St.result: result, 'description': description}

        description.write("\n{}\nIS NOT REFINABLE...".format(graph))
        if result is not None:
            result = response[St.result]
            description.write(" AS THE LINKSETS INVOLVED IN "
                              "THE LENS DO NOT SHARE THE SAME SPECIFICATIONS AS DESCRIBED BELOW ...")
            for i in range(1, len(result)):
                description.write("\n\n{:17}: {}".format(result[0][0], result[i][0]))
                description.write("\n{:17}: {}".format(result[0][1], result[i][1]))
                description.write("\n{:17}: {}".format(result[0][2], result[i][2]))
                description.write("\n{:17}: {}\n".format(result[0][3], result[i][3]))

            print description.getvalue()

        description.write(" {}".format(response[St.message]))
        print description.getvalue()
        return {St.message: False, St.result: response, 'description': description}

    description.write(" {}".format(response[St.message]))
    description.write("\n{}\nIS NOT REFINABLE...".format(graph))
    print description.getvalue()
    return {St.message: False, St.result: response, 'description': description}


# is_refinable("http://risis.eu/lens/union_Eter_2014_Amadeus_Orgref_20170703_P1252711024")
